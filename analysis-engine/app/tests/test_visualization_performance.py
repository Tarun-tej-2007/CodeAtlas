"""Unit test suite for Visualization Performance and Caching Framework."""

import unittest
import time
from unittest.mock import MagicMock

from app.graph import Graph as RepositoryGraph
from app.graph import GraphEdge, GraphMetadata, GraphNode
from app.graph.enums import EdgeType, NodeType
from app.visualization.exceptions import TransformationError
from app.visualization.pipeline import (
    TransformationStageError,
    VisualizationPipeline,
)
from app.visualization.transformers import VisualizationTransformer
from app.visualization.layouts import HierarchicalLayoutEngine
from app.visualization.serializer import VisualizationSerializer
from app.visualization.performance import (
    CacheError,
    InMemoryVisualizationCache,
    VisualizationMetrics,
    VisualizationProfiler,
    generate_graph_cache_key,
)


class TestVisualizationPerformanceFramework(unittest.TestCase):
    """Tests for Cache, Profiler, Metrics, and Pipeline Integration."""

    def setUp(self) -> None:
        self.cache = InMemoryVisualizationCache()
        self.profiler = VisualizationProfiler(enabled=True)

        self.transformer = VisualizationTransformer()
        self.layout_engine = HierarchicalLayoutEngine()
        self.serializer = VisualizationSerializer()

        self.pipeline = VisualizationPipeline(
            transformer=self.transformer,
            layout_engine=self.layout_engine,
            serializer=self.serializer,
            cache=self.cache,
            profiler=self.profiler,
        )

        # Construct a simple valid RepositoryGraph
        self.graph = RepositoryGraph(metadata=GraphMetadata(project_name="PerformanceProj"))
        n1 = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        n2 = GraphNode(id="n2", type=NodeType.FUNCTION, name="saveUser")
        edge = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.DECLARES)
        self.graph.add_node(n1)
        self.graph.add_node(n2)
        self.graph.add_edge(edge)

    def test_deterministic_cache_keys(self) -> None:
        key1 = generate_graph_cache_key(self.graph)

        # Re-construct identical graph structure (different object identities)
        graph2 = RepositoryGraph(metadata=GraphMetadata(project_name="PerformanceProj"))
        n1_dup = GraphNode(id="n1", type=NodeType.CLASS, name="UserService")
        n2_dup = GraphNode(id="n2", type=NodeType.FUNCTION, name="saveUser")
        edge_dup = GraphEdge(id="e1", source="n1", target="n2", type=EdgeType.DECLARES)
        graph2.add_node(n1_dup)
        graph2.add_node(n2_dup)
        graph2.add_edge(edge_dup)

        key2 = generate_graph_cache_key(graph2)
        self.assertEqual(key1, key2)

        # Modify metadata and ensure key changes
        graph3 = RepositoryGraph(metadata=GraphMetadata(project_name="PerformanceProjDiff"))
        graph3.add_node(n1_dup)
        graph3.add_node(n2_dup)
        graph3.add_edge(edge_dup)
        key3 = generate_graph_cache_key(graph3)
        self.assertNotEqual(key1, key3)

    def test_cache_hit_miss_and_stats(self) -> None:
        key = "test_key"
        val = {"test": "val"}

        # Miss
        self.assertIsNone(self.cache.get(key))
        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["size"], 0)

        # Set & Hit
        self.cache.set(key, val)
        self.assertEqual(self.cache.get(key), val)
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["size"], 1)

        # Overwrite
        val2 = {"another": "val"}
        self.cache.set(key, val2)
        self.assertEqual(self.cache.get(key), val2)

        # Invalidation
        self.cache.invalidate(key)
        self.assertIsNone(self.cache.get(key))
        stats = self.cache.get_stats()
        self.assertEqual(stats["invalidations"], 1)
        self.assertEqual(stats["size"], 0)

        # Clear
        self.cache.set(key, val)
        self.cache.clear()
        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["size"], 0)

    def test_profiler_timing(self) -> None:
        self.profiler.start("stage_a")
        time.sleep(0.005)
        duration = self.profiler.stop("stage_a")

        self.assertGreater(duration, 0.0)
        self.assertEqual(self.profiler.get_duration("stage_a"), duration)

        # Disabled profiler returns 0.0
        disabled = VisualizationProfiler(enabled=False)
        disabled.start("stage_a")
        self.assertEqual(disabled.stop("stage_a"), 0.0)

    def test_pipeline_cached_and_uncached_execution(self) -> None:
        # First execution (Uncached: Cache Miss)
        res1, metrics1 = self.pipeline.generate(self.graph, return_metrics=True)

        self.assertIsInstance(res1, dict)
        self.assertIsInstance(metrics1, VisualizationMetrics)
        self.assertTrue(metrics1.cache_miss)
        self.assertFalse(metrics1.cache_hit)
        self.assertEqual(metrics1.node_count, 2)
        self.assertEqual(metrics1.edge_count, 1)

        # Stats should show 1 miss
        stats = self.cache.get_stats()
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["hits"], 0)

        # Second execution (Cached: Cache Hit)
        res2, metrics2 = self.pipeline.generate(self.graph, return_metrics=True)
        self.assertEqual(res1, res2)
        self.assertTrue(metrics2.cache_hit)
        self.assertFalse(metrics2.cache_miss)

        stats = self.cache.get_stats()
        self.assertEqual(stats["hits"], 1)

        # Forced execution bypasses cache read but writes it
        res3, metrics3 = self.pipeline.generate(self.graph, force_compute=True, return_metrics=True)
        self.assertTrue(metrics3.cache_miss)
        self.assertFalse(metrics3.cache_hit)

    def test_cache_failure_raises_cache_error(self) -> None:
        faulty_cache = MagicMock()
        faulty_cache.get.side_effect = Exception("Disk error")

        pipeline = VisualizationPipeline(
            transformer=self.transformer,
            layout_engine=self.layout_engine,
            serializer=self.serializer,
            cache=faulty_cache,
        )

        with self.assertRaises(CacheError):
            pipeline.generate(self.graph)


if __name__ == "__main__":
    unittest.main()
