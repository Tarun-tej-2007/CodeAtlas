"""Visualization serializer module.

Provides VisualizationSerializer for converting VisualizationGraph aggregates to and from
portable dict and JSON formats.
"""

import json
from typing import Any
from pydantic import ValidationError

from app.visualization.exceptions import SerializationError
from app.visualization.models import VisualizationGraph


class VisualizationSerializer:
    """Serializes VisualizationGraph instances to/from JSON and dictionary representations."""

    @staticmethod
    def to_dict(graph: VisualizationGraph) -> dict[str, Any]:
        """Serializes a VisualizationGraph aggregate into a JSON-compatible dictionary.

        Args:
            graph: VisualizationGraph aggregate instance.

        Returns:
            Dictionary representation of the visualization.

        Raises:
            SerializationError: If serialization fails.
        """
        try:
            if not isinstance(graph, VisualizationGraph):
                raise SerializationError(f"Invalid visualization graph instance: {type(graph)}")

            return graph.model_dump(mode="json")
        except SerializationError:
            raise
        except Exception as err:
            raise SerializationError(f"Failed to serialize visualization to dict: {err}") from err

    @staticmethod
    def to_json(graph: VisualizationGraph, indent: int | None = 2) -> str:
        """Serializes a VisualizationGraph aggregate into a formatted JSON string.

        Args:
            graph: VisualizationGraph aggregate instance.
            indent: Optional JSON indentation spaces (defaults to 2).

        Returns:
            JSON string representation of the visualization.

        Raises:
            SerializationError: If serialization fails.
        """
        try:
            data = VisualizationSerializer.to_dict(graph)
            return json.dumps(data, indent=indent)
        except SerializationError:
            raise
        except Exception as err:
            raise SerializationError(f"Failed to serialize visualization to JSON: {err}") from err

    @staticmethod
    def from_dict(data: dict[str, Any]) -> VisualizationGraph:
        """Deserializes a VisualizationGraph aggregate from a dictionary.

        Args:
            data: Dictionary containing visualization graph keys.

        Returns:
            A reconstructed VisualizationGraph instance.

        Raises:
            SerializationError: If deserialization validation fails.
        """
        try:
            if not isinstance(data, dict):
                raise SerializationError(f"Expected dict data for deserialization, got: {type(data)}")

            if "metadata" not in data:
                raise SerializationError("Missing required 'metadata' key in visualization dictionary.")

            return VisualizationGraph.model_validate(data)
        except ValidationError as err:
            raise SerializationError(f"Malformed visualization validation error: {err}") from err
        except SerializationError:
            raise
        except Exception as err:
            raise SerializationError(f"Failed to deserialize visualization from dict: {err}") from err

    @staticmethod
    def from_json(json_str: str) -> VisualizationGraph:
        """Deserializes a VisualizationGraph aggregate from a JSON string.

        Args:
            json_str: Formatted or unformatted JSON string.

        Returns:
            A reconstructed VisualizationGraph instance.

        Raises:
            SerializationError: If JSON string is malformed or invalid.
        """
        try:
            if not isinstance(json_str, str) or not json_str.strip():
                raise SerializationError("Invalid or empty JSON string provided.")

            data = json.loads(json_str)
            return VisualizationSerializer.from_dict(data)
        except json.JSONDecodeError as err:
            raise SerializationError(f"Malformed JSON string: {err}") from err
        except SerializationError:
            raise
        except Exception as err:
            raise SerializationError(f"Failed to deserialize visualization from JSON: {err}") from err
