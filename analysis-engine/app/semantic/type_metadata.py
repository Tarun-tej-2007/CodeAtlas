"""Type metadata models and extraction interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.parser.models import ParsedFile
from app.semantic.models import SemanticSymbol


class TypeReference(BaseModel):
    """Represents a reference to a type, potentially including generic arguments and nullability."""

    name: str = Field(..., description="The declared name of the referenced type.")
    generic_arguments: List["TypeReference"] = Field(
        default_factory=list, description="Explicit generic argument type references."
    )
    is_nullable: bool = Field(default=False, description="Flag indicating if the type is explicitly declared nullable.")

    model_config = ConfigDict(frozen=True)


# Rebuild generic nested references in TypeReference
TypeReference.model_rebuild()


class TypeParameter(BaseModel):
    """Represents a generic type parameter definition (e.g. T in class Box<T>)."""

    name: str = Field(..., description="The name identifier of the generic type parameter.")
    constraint: Optional[TypeReference] = Field(default=None, description="Optional upper bound type constraint.")
    default: Optional[TypeReference] = Field(default=None, description="Optional default type fallback.")

    model_config = ConfigDict(frozen=True)


class InheritanceInfo(BaseModel):
    """Captures inheritance type structures (base classes and implemented interfaces)."""

    base_types: List[TypeReference] = Field(
        default_factory=list, description="Collection of extended base type references."
    )
    implemented_interfaces: List[TypeReference] = Field(
        default_factory=list, description="Collection of implemented interface references."
    )

    model_config = ConfigDict(frozen=True)


class DecoratorInfo(BaseModel):
    """Represents metadata annotations/decorators declared on symbols (e.g. @Component)."""

    name: str = Field(..., description="The name of the decorator.")
    arguments: List[str] = Field(
        default_factory=list, description="Stringified argument list values passed to the decorator."
    )

    model_config = ConfigDict(frozen=True)


class ModifierInfo(BaseModel):
    """Describes modifier keywords explicitly associated with declaration headers."""

    is_static: bool = Field(default=False, description="Declaration is static/class-bound.")
    is_async: bool = Field(default=False, description="Declaration is asynchronous.")
    is_readonly: bool = Field(default=False, description="Declaration is read-only / final.")
    is_abstract: bool = Field(default=False, description="Declaration is abstract.")

    model_config = ConfigDict(frozen=True)


class ParameterInfo(BaseModel):
    """Describes method or function parameter signature specifications."""

    name: str = Field(..., description="Name identifier of the parameter.")
    type_annotation: Optional[TypeReference] = Field(
        default=None, description="Explicit type annotation for the parameter."
    )
    is_optional: bool = Field(default=False, description="Flag indicating if the parameter is optional.")
    default_value: Optional[str] = Field(
        default=None, description="String representation of the default argument expression value."
    )

    model_config = ConfigDict(frozen=True)


class MethodSignature(BaseModel):
    """Represents structural method signature specifications."""

    name: str = Field(..., description="Name identifier of the method.")
    parameters: List[ParameterInfo] = Field(default_factory=list, description="Ordered parameters list.")
    return_type: Optional[TypeReference] = Field(default=None, description="Explicit return type annotation.")
    type_parameters: List[TypeParameter] = Field(
        default_factory=list, description="Generic type parameter constraints."
    )
    modifiers: ModifierInfo = Field(default_factory=ModifierInfo, description="Modifier keywords info.")
    decorators: List[DecoratorInfo] = Field(default_factory=list, description="Decorators list.")

    model_config = ConfigDict(frozen=True)


class PropertySignature(BaseModel):
    """Represents class field or interface property specifications."""

    name: str = Field(..., description="Name identifier of the property.")
    type_annotation: Optional[TypeReference] = Field(default=None, description="Explicit type annotation.")
    modifiers: ModifierInfo = Field(default_factory=ModifierInfo, description="Modifier keywords info.")
    decorators: List[DecoratorInfo] = Field(default_factory=list, description="Decorators list.")

    model_config = ConfigDict(frozen=True)


class TypeMetadataExtractor(ABC):
    """Abstract interface defining the contract for extracting explicit type metadata from parsed code ASTs."""

    @abstractmethod
    def extract_type_metadata(self, parsed_file: ParsedFile, symbol: SemanticSymbol) -> Dict[str, Any]:
        """Extracts explicit type metadata associated with a given SemanticSymbol.

        Args:
            parsed_file: The parsed file representation containing AST nodes.
            symbol: The semantic symbol to extract type metadata details for.

        Returns:
            A dictionary containing parsed type metadata fields (e.g. parameters, return types).
        """
        pass
