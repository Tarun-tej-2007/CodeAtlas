"""Graph serializer module.

Provides GraphSerializer for converting Graph containers to and from portable dict
and JSON formats with validation and order preservation.
"""

import json
from typing import Any
from pydantic import ValidationError

from app.graph.exceptions import GraphError
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphMetadata, GraphNode
from app.graph.serialization.exceptions import GraphSerializationError
from app.graph.serialization.models import SerializedGraph


class GraphSerializer:
    """Serializes Graph instances to/from JSON and dictionary representations."""

    @staticmethod
    def to_dict(graph: Graph) -> dict[str, Any]:
        """Serializes a Graph container into a JSON-compatible dictionary.

        Args:
            graph: Graph instance to serialize.

        Returns:
            Dictionary containing metadata, nodes, and edges.

        Raises:
            GraphSerializationError: If graph is invalid or serialization fails.
        """
        try:
            if not isinstance(graph, Graph):
                raise GraphSerializationError(f"Invalid graph instance: {type(graph)}")

            serialized = SerializedGraph(
                metadata=graph.metadata,
                nodes=graph.nodes,
                edges=graph.edges,
            )
            return serialized.model_dump(mode="json")
        except GraphSerializationError:
            raise
        except Exception as err:
            raise GraphSerializationError(f"Failed to serialize graph to dict: {err}") from err

    @staticmethod
    def to_json(graph: Graph, indent: int | None = 2) -> str:
        """Serializes a Graph container into a formatted JSON string.

        Args:
            graph: Graph instance to serialize.
            indent: Optional JSON indentation spaces (defaults to 2).

        Returns:
            JSON string representation of the graph.

        Raises:
            GraphSerializationError: If serialization fails.
        """
        try:
            data = GraphSerializer.to_dict(graph)
            return json.dumps(data, indent=indent)
        except GraphSerializationError:
            raise
        except Exception as err:
            raise GraphSerializationError(f"Failed to serialize graph to JSON: {err}") from err

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Graph:
        """Deserializes a Graph container from a dictionary.

        Args:
            data: Dictionary containing metadata, nodes, and edges keys.

        Returns:
            A reconstructed Graph container.

        Raises:
            GraphSerializationError: If data format is invalid, malformed, or contains duplicate/invalid references.
        """
        try:
            if not isinstance(data, dict):
                raise GraphSerializationError(f"Expected dict data for graph deserialization, got: {type(data)}")

            if "metadata" not in data:
                raise GraphSerializationError("Missing required 'metadata' key in graph dictionary.")
            if "nodes" not in data:
                raise GraphSerializationError("Missing required 'nodes' key in graph dictionary.")
            if "edges" not in data:
                raise GraphSerializationError("Missing required 'edges' key in graph dictionary.")

            serialized = SerializedGraph.model_validate(data)

            graph = Graph(metadata=serialized.metadata)

            # Add nodes
            for node in serialized.nodes:
                try:
                    graph.add_node(node)
                except GraphError as err:
                    raise GraphSerializationError(f"Deserialization node error: {err}") from err

            # Add edges
            for edge in serialized.edges:
                try:
                    graph.add_edge(edge)
                except GraphError as err:
                    raise GraphSerializationError(f"Deserialization edge error: {err}") from err

            return graph
        except ValidationError as err:
            raise GraphSerializationError(f"Malformed graph validation error: {err}") from err
        except GraphSerializationError:
            raise
        except Exception as err:
            raise GraphSerializationError(f"Failed to deserialize graph from dict: {err}") from err

    @staticmethod
    def from_json(json_str: str) -> Graph:
        """Deserializes a Graph container from a JSON string.

        Args:
            json_str: Formatted or unformatted JSON string.

        Returns:
            A reconstructed Graph container.

        Raises:
            GraphSerializationError: If JSON string is malformed or invalid.
        """
        try:
            if not isinstance(json_str, str) or not json_str.strip():
                raise GraphSerializationError("Invalid or empty JSON string provided.")

            data = json.loads(json_str)
            return GraphSerializer.from_dict(data)
        except json.JSONDecodeError as err:
            raise GraphSerializationError(f"Malformed JSON string: {err}") from err
        except GraphSerializationError:
            raise
        except Exception as err:
            raise GraphSerializationError(f"Failed to deserialize graph from JSON: {err}") from err
