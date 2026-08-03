"""Unit tests for the Layer Detection Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from app.graph.enums import DependencyNodeType
from app.graph.dependency_models import DependencyMetadata, GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.architecture.enums import LayerType
from app.architecture.layer_detector import LayerRule, LayerDetector


class TestLayerDetector(unittest.TestCase):
    """Verifies stateless layer detection, sorting determinism, and thread-safety contract."""

    def setUp(self) -> None:
        # Predefined rule set
        self.rules = [
            LayerRule(
                layer_id="presentation",
                layer_name="Presentation Layer",
                layer_type=LayerType.PRESENTATION,
                id_patterns=[r".*/controllers/.*", r".*/views/.*"],
                metadata_patterns={"framework": "fastapi"}
            ),
            LayerRule(
                layer_id="domain",
                layer_name="Domain Layer",
                layer_type=LayerType.DOMAIN,
                name_patterns=[r".*Entity$", r".*Aggregate$"],
                types=[DependencyNodeType.CLASS]
            ),
            LayerRule(
                layer_id="infrastructure",
                layer_name="Infrastructure Layer",
                layer_type=LayerType.INFRASTRUCTURE,
                id_patterns=[r".*/db/.*", r".*/client/.*"],
                metadata={"db": "postgres"}
            )
        ]
        self.detector = LayerDetector(self.rules)

    def test_empty_graph(self) -> None:
        graph = DependencyGraph(nodes=[], edges=[])
        layers = self.detector.detect_layers(graph)
        self.assertEqual(layers, [])

    def test_single_layer_assignment(self) -> None:
        node = GraphNode(
            id="src/controllers/user.py",
            name="UserController",
            type=DependencyNodeType.MODULE
        )
        graph = DependencyGraph(nodes=[node], edges=[])
        layers = self.detector.detect_layers(graph)
        
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].id, "presentation")
        self.assertEqual(layers[0].layer_type, LayerType.PRESENTATION)
        self.assertEqual(layers[0].node_ids, ["src/controllers/user.py"])

    def test_multiple_layers_assignment(self) -> None:
        node_pres = GraphNode(
            id="src/controllers/user.py",
            name="UserController",
            type=DependencyNodeType.MODULE
        )
        node_dom = GraphNode(
            id="src/models/user.py",
            name="UserEntity",
            type=DependencyNodeType.CLASS
        )
        node_infra = GraphNode(
            id="src/db/session.py",
            name="Session",
            type=DependencyNodeType.MODULE
        )
        
        graph = DependencyGraph(
            nodes=[node_pres, node_dom, node_infra],
            edges=[]
        )
        layers = self.detector.detect_layers(graph)

        # 3 layers should be generated, sorted by ID: domain, infrastructure, presentation
        self.assertEqual(len(layers), 3)
        self.assertEqual(layers[0].id, "domain")
        self.assertEqual(layers[1].id, "infrastructure")
        self.assertEqual(layers[2].id, "presentation")

        self.assertEqual(layers[0].node_ids, ["src/models/user.py"])
        self.assertEqual(layers[1].node_ids, ["src/db/session.py"])
        self.assertEqual(layers[2].node_ids, ["src/controllers/user.py"])

    def test_unknown_layer_fallback(self) -> None:
        node_known = GraphNode(
            id="src/controllers/user.py",
            name="UserController",
            type=DependencyNodeType.MODULE
        )
        node_unknown = GraphNode(
            id="src/misc/helpers.py",
            name="helpers",
            type=DependencyNodeType.MODULE
        )
        
        graph = DependencyGraph(nodes=[node_known, node_unknown], edges=[])
        layers = self.detector.detect_layers(graph)

        # 2 layers: presentation, unknown
        self.assertEqual(len(layers), 2)
        self.assertEqual(layers[0].id, "presentation")
        self.assertEqual(layers[1].id, "unknown")
        self.assertEqual(layers[1].layer_type, LayerType.UNKNOWN)
        self.assertEqual(layers[1].node_ids, ["src/misc/helpers.py"])

    def test_deterministic_ordering(self) -> None:
        # Check that list of nodes inside layer is sorted lexicographically
        node1 = GraphNode(
            id="src/db/queries.py",
            name="queries",
            type=DependencyNodeType.MODULE
        )
        node2 = GraphNode(
            id="src/db/connection.py",
            name="connection",
            type=DependencyNodeType.MODULE
        )
        
        # Insert nodes in random order
        graph = DependencyGraph(nodes=[node1, node2], edges=[])
        layers = self.detector.detect_layers(graph)

        self.assertEqual(len(layers), 1)
        # Expected node IDs sorted: connection.py then queries.py
        self.assertEqual(
            layers[0].node_ids,
            ["src/db/connection.py", "src/db/queries.py"]
        )

    def test_metadata_preservation(self) -> None:
        node = GraphNode(
            id="src/db/session.py",
            name="Session",
            type=DependencyNodeType.MODULE
        )
        graph = DependencyGraph(nodes=[node], edges=[])
        layers = self.detector.detect_layers(graph)

        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].metadata, {"db": "postgres"})

    def test_stateless_repeated_execution(self) -> None:
        node = GraphNode(
            id="src/controllers/user.py",
            name="UserController",
            type=DependencyNodeType.MODULE
        )
        graph = DependencyGraph(nodes=[node], edges=[])
        
        # Verify multiple runs yield identical outcomes
        res1 = self.detector.detect_layers(graph)
        res2 = self.detector.detect_layers(graph)
        self.assertEqual(res1, res2)

    def test_thread_safety(self) -> None:
        node = GraphNode(
            id="src/controllers/user.py",
            name="UserController",
            type=DependencyNodeType.MODULE
        )
        graph = DependencyGraph(nodes=[node], edges=[])

        def run_detector():
            return self.detector.detect_layers(graph)

        # Run detection in parallel across 8 concurrent threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_detector) for _ in range(20)]
            results = [f.result() for f in futures]

        # Verify all thread runs returned exact identical, correct answers
        first = results[0]
        self.assertEqual(first[0].id, "presentation")
        for res in results:
            self.assertEqual(res, first)


if __name__ == "__main__":
    unittest.main()
