"""Unit test suite for visualization domain enumerations."""

import unittest
from app.visualization import EdgeKind, GroupKind, LayoutKind, NodeKind


class TestVisualizationEnums(unittest.TestCase):
    """Tests for NodeKind, EdgeKind, LayoutKind, and GroupKind enumerations."""

    def test_node_kind_values(self) -> None:
        self.assertEqual(NodeKind.MODULE, "module")
        self.assertEqual(NodeKind.CLASS, "class")
        self.assertEqual(NodeKind.FUNCTION, "function")
        self.assertEqual(NodeKind.METHOD, "method")
        self.assertEqual(NodeKind.VARIABLE, "variable")
        self.assertEqual(NodeKind.PACKAGE, "package")
        self.assertEqual(NodeKind.INTERFACE, "interface")
        self.assertEqual(NodeKind.ENUM, "enum")
        self.assertEqual(NodeKind.UNKNOWN, "unknown")

    def test_edge_kind_values(self) -> None:
        self.assertEqual(EdgeKind.CALL, "call")
        self.assertEqual(EdgeKind.IMPORT, "import")
        self.assertEqual(EdgeKind.INHERITANCE, "inheritance")
        self.assertEqual(EdgeKind.REFERENCE, "reference")
        self.assertEqual(EdgeKind.CONTAINS, "contains")

    def test_layout_kind_values(self) -> None:
        self.assertEqual(LayoutKind.NONE, "none")
        self.assertEqual(LayoutKind.HIERARCHICAL, "hierarchical")
        self.assertEqual(LayoutKind.FORCE_DIRECTED, "force_directed")
        self.assertEqual(LayoutKind.RADIAL, "radial")
        self.assertEqual(LayoutKind.GRID, "grid")

    def test_group_kind_values(self) -> None:
        self.assertEqual(GroupKind.PACKAGE, "package")
        self.assertEqual(GroupKind.DIRECTORY, "directory")
        self.assertEqual(GroupKind.MODULE, "module")
        self.assertEqual(GroupKind.NAMESPACE, "namespace")


if __name__ == "__main__":
    unittest.main()
