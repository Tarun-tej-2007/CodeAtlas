"""Unit test suite for GraphQueryEngine O(1) lookups, filtering, and structural/behavioral traversals."""

from pathlib import Path
import unittest

from app.graph import (
    EdgeType,
    Graph,
    GraphEdge,
    GraphNode,
    NodeType,
)
from app.graph.query import (
    GraphQueryEngine,
    GraphQueryError,
    filter_edges,
    filter_nodes,
)


class TestGraphQueryEngine(unittest.TestCase):
    """Tests for GraphQueryEngine queries, traversals, helpers, and exception handling."""

    def setUp(self) -> None:
        self.graph = Graph()

        # Build sample graph hierarchy
        self.project_node = GraphNode(id="proj_1", type=NodeType.PROJECT, name="TestProject")
        self.file_node = GraphNode(id="file_1", type=NodeType.FILE, name="app.js", path=Path("/repo/app.js"))
        self.module_node = GraphNode(id="mod_1", type=NodeType.MODULE, name="app")

        self.class_node = GraphNode(id="cls_1", type=NodeType.CLASS, name="UserService", path=Path("/repo/app.js"), line=5)
        self.method_node = GraphNode(id="meth_1", type=NodeType.METHOD, name="save", path=Path("/repo/app.js"), line=10)
        self.param_node = GraphNode(id="param_1", type=NodeType.PARAMETER, name="user", path=Path("/repo/app.js"), line=10)

        self.fn_caller = GraphNode(id="fn_1", type=NodeType.FUNCTION, name="main", path=Path("/repo/app.js"), line=20)
        self.fn_callee = GraphNode(id="fn_2", type=NodeType.FUNCTION, name="helper", path=Path("/repo/app.js"), line=30)

        self.ext_mod = GraphNode(id="mod_ext", type=NodeType.MODULE, name="react")

        # Add nodes
        for n in [
            self.project_node, self.file_node, self.module_node,
            self.class_node, self.method_node, self.param_node,
            self.fn_caller, self.fn_callee, self.ext_mod
        ]:
            self.graph.add_node(n)

        # Add structural edges
        self.graph.add_edge(GraphEdge(id="e_proj_file", source="proj_1", target="file_1", type=EdgeType.CONTAINS))
        self.graph.add_edge(GraphEdge(id="e_file_cls", source="file_1", target="cls_1", type=EdgeType.DECLARES))
        self.graph.add_edge(GraphEdge(id="e_file_caller", source="file_1", target="fn_1", type=EdgeType.DECLARES))
        self.graph.add_edge(GraphEdge(id="e_file_callee", source="file_1", target="fn_2", type=EdgeType.DECLARES))

        self.graph.add_edge(GraphEdge(id="e_cls_meth", source="cls_1", target="meth_1", type=EdgeType.DECLARES))
        self.graph.add_edge(GraphEdge(id="e_meth_param", source="meth_1", target="param_1", type=EdgeType.OWNS))

        # Add behavioral call edges
        self.graph.add_edge(GraphEdge(id="e_call_main_helper", source="fn_1", target="fn_2", type=EdgeType.CALLS))
        self.graph.add_edge(GraphEdge(id="e_call_main_meth", source="fn_1", target="meth_1", type=EdgeType.CALLS))

        # Add dependency edges
        self.graph.add_edge(GraphEdge(id="e_imp_mod_react", source="mod_1", target="mod_ext", type=EdgeType.IMPORTS))
        self.graph.add_edge(GraphEdge(id="e_exp_mod_cls", source="mod_1", target="cls_1", type=EdgeType.EXPORTS))

        self.qe = GraphQueryEngine(self.graph)

    def test_node_and_edge_queries(self) -> None:
        node = self.qe.get_node("cls_1")
        self.assertEqual(node.name, "UserService")

        classes = self.qe.get_nodes_by_type(NodeType.CLASS)
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].name, "UserService")

        found = self.qe.find_node_by_name("main")
        self.assertIsNotNone(found)
        self.assertEqual(found.id, "fn_1")  # type: ignore

        all_edges = self.qe.get_edges()
        self.assertGreater(len(all_edges), 5)

        call_edges = self.qe.get_edges_by_type(EdgeType.CALLS)
        self.assertEqual(len(call_edges), 2)

    def test_graph_traversal(self) -> None:
        parents_cls = self.qe.parents("cls_1")
        self.assertEqual(len(parents_cls), 1)
        self.assertEqual(parents_cls[0].id, "file_1")

        children_cls = self.qe.children("cls_1")
        self.assertEqual(len(children_cls), 1)
        self.assertEqual(children_cls[0].id, "meth_1")

        succ_fn1 = self.qe.successors("fn_1")
        self.assertEqual(len(succ_fn1), 2)
        succ_ids = {n.id for n in succ_fn1}
        self.assertIn("fn_2", succ_ids)
        self.assertIn("meth_1", succ_ids)

        pred_meth1 = self.qe.predecessors("meth_1")
        pred_ids = {n.id for n in pred_meth1}
        self.assertIn("cls_1", pred_ids)
        self.assertIn("fn_1", pred_ids)

    def test_structural_and_behavioral_helpers(self) -> None:
        file_syms = self.qe.get_file_symbols("file_1")
        self.assertGreaterEqual(len(file_syms), 3)

        class_members = self.qe.get_class_members("cls_1")
        self.assertEqual(len(class_members), 1)
        self.assertEqual(class_members[0].id, "meth_1")

        params = self.qe.get_function_parameters("meth_1")
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "user")

        callers = self.qe.get_callers("fn_2")
        self.assertEqual(len(callers), 1)
        self.assertEqual(callers[0].name, "main")

        callees = self.qe.get_callees("fn_1")
        self.assertEqual(len(callees), 2)

    def test_dependency_helpers(self) -> None:
        imports = self.qe.get_imports("mod_1")
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].name, "react")

        exports = self.qe.get_exports("mod_1")
        self.assertEqual(len(exports), 1)
        self.assertEqual(exports[0].name, "UserService")

    def test_invalid_query_raises_graph_query_error(self) -> None:
        with self.assertRaises(GraphQueryError):
            self.qe.get_node("non_existent_id")

        with self.assertRaises(GraphQueryError):
            self.qe.get_outgoing_edges("non_existent_id")

    def test_empty_graph_query(self) -> None:
        empty_qe = GraphQueryEngine(Graph())
        self.assertEqual(len(empty_qe.get_nodes()), 0)
        self.assertEqual(len(empty_qe.get_edges()), 0)


if __name__ == "__main__":
    unittest.main()
