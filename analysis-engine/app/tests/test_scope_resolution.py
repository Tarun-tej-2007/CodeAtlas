"""Unit tests for the ScopeNode and ScopeManager classes."""

import unittest

from app.semantic.enums import ScopeKind
from app.semantic.exceptions import SemanticResolutionError, SemanticModelError
from app.semantic import (
    ScopeNode,
    ScopeManager,
    Location,
)


class TestScopeResolution(unittest.TestCase):
    """Tests lexical scope nesting, stack transitions, boundaries, and query helpers."""

    def test_scope_creation(self) -> None:
        # Scope creation
        loc = Location(start_line=1, start_column=0, end_line=10, end_column=5)
        scope = ScopeNode(id="my-scope", kind=ScopeKind.CLASS, location=loc, metadata={"class_type": "dataclass"})
        
        self.assertEqual(scope.id, "my-scope")
        self.assertEqual(scope.kind, ScopeKind.CLASS)
        self.assertEqual(scope.location, loc)
        self.assertEqual(scope.metadata["class_type"], "dataclass")
        self.assertEqual(len(scope.children), 0)
        self.assertEqual(len(scope.symbol_ids), 0)

    def test_scope_manager_basic_flow_and_nesting(self) -> None:
        # Initialize
        manager = ScopeManager(root_id="global-root")
        
        # root scope retrieval
        root = manager.get_root_scope()
        self.assertEqual(root.id, "global-root")
        self.assertEqual(manager.get_current_scope(), root)
        self.assertEqual(manager.stack, [root])

        # nested scopes creation
        class_scope = manager.create_scope(id="ClassA", kind=ScopeKind.CLASS)
        self.assertEqual(class_scope.parent, root)
        self.assertIn(class_scope, root.children)
        self.assertEqual(manager.get_child_scopes("global-root"), [class_scope])

        # entering/exiting scopes
        manager.enter_scope(class_scope)
        self.assertEqual(manager.get_current_scope(), class_scope)
        self.assertEqual(manager.stack, [root, class_scope])

        # create a scope inside ClassA
        method_scope = manager.create_scope(id="method_1", kind=ScopeKind.METHOD)
        self.assertEqual(method_scope.parent, class_scope)
        manager.enter_scope(method_scope)
        self.assertEqual(manager.get_current_scope(), method_scope)
        self.assertEqual(manager.stack, [root, class_scope, method_scope])

        # parent lookup
        parents = manager.get_parent_scopes("method_1")
        self.assertEqual(parents, [class_scope, root])

        # exiting scope
        manager.exit_scope()
        self.assertEqual(manager.get_current_scope(), class_scope)
        self.assertEqual(manager.stack, [root, class_scope])

        manager.exit_scope()
        self.assertEqual(manager.get_current_scope(), root)
        self.assertEqual(manager.stack, [root])

    def test_invalid_transitions_and_empty_stack_behavior(self) -> None:
        manager = ScopeManager()

        # empty stack behavior: exiting root scope raising error
        with self.assertRaises(SemanticResolutionError):
            manager.exit_scope()

        # invalid scope transitions: entering unregistered scope
        unregistered = ScopeNode(id="ghost", kind=ScopeKind.BLOCK)
        with self.assertRaises(SemanticResolutionError):
            manager.enter_scope(unregistered)

        # duplicate scope ID registration raises SemanticModelError
        manager.create_scope(id="nested-1", kind=ScopeKind.BLOCK)
        with self.assertRaises(SemanticModelError):
            manager.create_scope(id="nested-1", kind=ScopeKind.BLOCK)

    def test_symbol_registration_and_lookup(self) -> None:
        manager = ScopeManager()
        root = manager.get_root_scope()

        # symbol registration in current scope
        manager.register_symbol("global_var")
        self.assertIn("global_var", root.symbol_ids)

        # nested scope symbol registration
        class_scope = manager.create_scope(id="ClassB", kind=ScopeKind.CLASS)
        manager.enter_scope(class_scope)
        manager.register_symbol("class_field")
        self.assertIn("class_field", class_scope.symbol_ids)

        # lookup symbol scope
        # 'class_field' is in current (ClassB) scope
        self.assertEqual(manager.lookup_symbol_scope("class_field"), class_scope)
        # 'global_var' is found by searching up to parent (global)
        self.assertEqual(manager.lookup_symbol_scope("global_var"), root)
        # Unregistered symbol returns None
        self.assertIsNone(manager.lookup_symbol_scope("unknown_var"))

        # child scope relationships check
        self.assertEqual(manager.get_child_scopes("ClassB"), [])


if __name__ == "__main__":
    unittest.main()
