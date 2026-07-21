"""Call graph builder module.

Provides CallGraphBuilder for enriching an existing structural Graph with
behavioral EdgeType.CALLS relationships using CallAnalysisResult objects.
"""

from typing import Any
from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.models import AnalysisContext
from app.graph.builder import BaseGraphBuilder
from app.graph.enums import EdgeType
from app.graph.exceptions import GraphBuilderError, GraphError
from app.graph.graph import Graph
from app.graph.models import GraphEdge


class CallGraphBuilder(BaseGraphBuilder):
    """Builder that enriches an existing Graph container with CALLS edges."""

    def __init__(self) -> None:
        """Initializes CallGraphBuilder."""
        pass

    def build(
        self,
        graph: Graph | Any,
        context: AnalysisContext | list[AnalysisContext] | Any = None,
        call_result: CallAnalysisResult | list[CallAnalysisResult] | Any = None,
    ) -> Graph:
        """Enriches an existing Graph container with CALLS edges from CallAnalysisResult objects.

        Args:
            graph: Existing Graph container to enrich.
            context: AnalysisContext or list of AnalysisContext objects (optional if call_result is provided).
            call_result: CallAnalysisResult or list of CallAnalysisResult objects.

        Returns:
            The enriched Graph container.

        Raises:
            GraphBuilderError: If graph or call results are invalid.
        """
        try:
            if not isinstance(graph, Graph):
                raise GraphBuilderError(f"Invalid graph instance provided to CallGraphBuilder: {type(graph)}")

            results: list[CallAnalysisResult] = []
            if isinstance(call_result, CallAnalysisResult):
                results = [call_result]
            elif isinstance(call_result, (list, tuple)):
                results = [r for r in call_result if isinstance(r, CallAnalysisResult)]

            # If call_result was omitted, attempt to find call results in contexts
            if not results and context:
                contexts = [context] if isinstance(context, AnalysisContext) else (context if isinstance(context, (list, tuple)) else [])
                # If callers passed call results as 2nd arg
                for c in contexts:
                    if isinstance(c, CallAnalysisResult):
                        results.append(c)

            if not results and not isinstance(call_result, (list, tuple)):
                # If call_result was passed as second positional argument
                if isinstance(context, CallAnalysisResult):
                    results = [context]

            added_edge_ids: set[str] = set()

            for res in results:
                if not res or not res.calls:
                    continue

                for call in res.calls:
                    # Ignore unresolved calls to avoid dangling edges
                    if not call.resolved or not call.callee_symbol_id:
                        continue

                    callee_id = call.callee_symbol_id
                    # Ensure target callee node exists in graph
                    if graph.get_node(callee_id) is None:
                        continue

                    # Determine caller source node ID
                    caller_id = call.caller_symbol_id
                    if not caller_id or graph.get_node(caller_id) is None:
                        # Fallback to file node if caller is top-level
                        file_node_id = f"file_{str(call.path.name).replace('.', '_')}"
                        file_candidates = [n for n in graph.nodes if n.path == call.path]
                        if file_candidates:
                            caller_id = file_candidates[0].id
                        elif graph.get_node(file_node_id) is not None:
                            caller_id = file_node_id
                        else:
                            # Skip if neither caller symbol nor file node exist in graph
                            continue

                    # Generate deterministic edge ID
                    edge_id = f"edge_calls_{caller_id}_{callee_id}_{call.line}_{call.column}"

                    if edge_id in added_edge_ids or graph.get_edge(edge_id) is not None:
                        continue

                    calls_edge = GraphEdge(
                        id=edge_id,
                        source=caller_id,
                        target=callee_id,
                        type=EdgeType.CALLS,
                        metadata={
                            "kind": call.kind.value,
                            "line": call.line,
                            "column": call.column,
                        },
                    )
                    graph.add_edge(calls_edge)
                    added_edge_ids.add(edge_id)

            return graph
        except GraphError as err:
            raise GraphBuilderError(f"Call graph enrichment failed: {err}") from err
        except GraphBuilderError:
            raise
        except Exception as err:
            raise GraphBuilderError(f"Failed to build call graph: {err}") from err
