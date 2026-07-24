"""Unit tests for the Type Metadata models and extractors."""

import unittest
from pydantic import ValidationError

from app.semantic import (
    TypeReference,
    TypeParameter,
    InheritanceInfo,
    DecoratorInfo,
    ModifierInfo,
    ParameterInfo,
    MethodSignature,
    PropertySignature,
)


class TestTypeMetadata(unittest.TestCase):
    """Tests model validation, nesting generic arguments, modifiers, serialization, and immutability."""

    def test_type_reference_and_generics(self) -> None:
        # Construct type reference with nested generic arguments
        # e.g., Map<String, List<Integer>>?
        inner_list = TypeReference(name="List", generic_arguments=[TypeReference(name="Integer")])
        map_ref = TypeReference(
            name="Map",
            generic_arguments=[TypeReference(name="String"), inner_list],
            is_nullable=True
        )

        self.assertEqual(map_ref.name, "Map")
        self.assertEqual(len(map_ref.generic_arguments), 2)
        self.assertEqual(map_ref.generic_arguments[0].name, "String")
        self.assertEqual(map_ref.generic_arguments[1].name, "List")
        self.assertEqual(map_ref.generic_arguments[1].generic_arguments[0].name, "Integer")
        self.assertTrue(map_ref.is_nullable)

    def test_serialization_and_immutability(self) -> None:
        decorator = DecoratorInfo(name="Inject", arguments=["'AuthService'"])
        
        # Verify serialization
        data = decorator.model_dump()
        self.assertEqual(data["name"], "Inject")
        self.assertEqual(data["arguments"], ["'AuthService'"])

        # Verify immutability (frozen BaseModel raising ValidationError or TypeError)
        with self.assertRaises((ValidationError, TypeError)):
            decorator.name = "Modified"  # type: ignore

    def test_inheritance_metadata(self) -> None:
        base_class = TypeReference(name="BaseView")
        interface1 = TypeReference(name="IComponent")
        interface2 = TypeReference(name="IDisposable")

        inheritance = InheritanceInfo(
            base_types=[base_class],
            implemented_interfaces=[interface1, interface2]
        )

        self.assertEqual(len(inheritance.base_types), 1)
        self.assertEqual(inheritance.base_types[0].name, "BaseView")
        self.assertEqual(len(inheritance.implemented_interfaces), 2)
        self.assertEqual(inheritance.implemented_interfaces[0].name, "IComponent")
        self.assertEqual(inheritance.implemented_interfaces[1].name, "IDisposable")

    def test_modifiers_and_defaults(self) -> None:
        # Modifier defaults
        modifiers = ModifierInfo()
        self.assertFalse(modifiers.is_static)
        self.assertFalse(modifiers.is_async)
        self.assertFalse(modifiers.is_readonly)
        self.assertFalse(modifiers.is_abstract)

        # Custom values
        custom_modifiers = ModifierInfo(is_static=True, is_async=True, is_abstract=True)
        self.assertTrue(custom_modifiers.is_static)
        self.assertTrue(custom_modifiers.is_async)
        self.assertTrue(custom_modifiers.is_abstract)
        self.assertFalse(custom_modifiers.is_readonly)

    def test_method_and_property_signatures(self) -> None:
        param = ParameterInfo(
            name="userId",
            type_annotation=TypeReference(name="string"),
            is_optional=True,
            default_value="''"
        )
        
        method = MethodSignature(
            name="fetchUser",
            parameters=[param],
            return_type=TypeReference(name="Promise", generic_arguments=[TypeReference(name="User")]),
            type_parameters=[TypeParameter(name="T", constraint=TypeReference(name="User"))],
            modifiers=ModifierInfo(is_async=True, is_static=False),
            decorators=[DecoratorInfo(name="Log")]
        )

        self.assertEqual(method.name, "fetchUser")
        self.assertTrue(method.modifiers.is_async)
        self.assertEqual(len(method.parameters), 1)
        self.assertEqual(method.parameters[0].name, "userId")
        self.assertEqual(method.parameters[0].type_annotation.name, "string")
        self.assertTrue(method.parameters[0].is_optional)
        self.assertEqual(method.parameters[0].default_value, "''")
        self.assertEqual(method.return_type.name, "Promise")
        self.assertEqual(method.return_type.generic_arguments[0].name, "User")
        self.assertEqual(len(method.type_parameters), 1)
        self.assertEqual(method.type_parameters[0].name, "T")
        self.assertEqual(method.type_parameters[0].constraint.name, "User")
        self.assertEqual(len(method.decorators), 1)
        self.assertEqual(method.decorators[0].name, "Log")

        prop = PropertySignature(
            name="config",
            type_annotation=TypeReference(name="AppConfig"),
            modifiers=ModifierInfo(is_readonly=True)
        )
        self.assertEqual(prop.name, "config")
        self.assertTrue(prop.modifiers.is_readonly)


if __name__ == "__main__":
    unittest.main()
