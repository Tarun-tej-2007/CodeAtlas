"""Visualization pipeline orchestrator module.

Combines transformation, layout, and serialization stages into a single unified pipeline.
"""

from typing import Any
from app.graph import Graph
from app.visualization.exceptions import (
    TransformationError,
    SerializationError,
)
from app.visualization.layouts.exceptions import LayoutEngineError
from app.visualization.pipeline.exceptions import (
    LayoutStageError,
    SerializationStageError,
    TransformationStageError,
    VisualizationPipelineError,
)
from app.visualization.performance import (
    generate_graph_cache_key,
    VisualizationMetrics,
    VisualizationProfiler,
    CacheError,
)


class VisualizationPipeline:
    """Orchestrates transformation, layout placement, and serialization of a RepositoryGraph."""

    def __init__(
        self,
        transformer: Any,
        layout_engine: Any,
        serializer: Any,
        cache: Any = None,
        profiler: Any = None,
    ) -> None:
        """Initializes VisualizationPipeline with injected dependencies.

        Args:
            transformer: Object satisfying the transform method (e.g. VisualizationTransformer).
            layout_engine: Object satisfying the layout method (e.g. BaseLayoutEngine).
            serializer: Object satisfying serialization to_dict / to_json (e.g. VisualizationSerializer).
            cache: Optional VisualizationCache provider.
            profiler: Optional VisualizationProfiler provider.
        """
        self.transformer = transformer
        self.layout_engine = layout_engine
        self.serializer = serializer
        self.cache = cache
        self.profiler = profiler

    def generate(
        self,
        graph: Graph,
        force_compute: bool = False,
        return_metrics: bool = False,
    ) -> dict[str, Any] | tuple[dict[str, Any], VisualizationMetrics]:
        """Generates a fully positioned and serialized visualization from a RepositoryGraph.

        Args:
            graph: RepositoryGraph instance.
            force_compute: If True, bypasses cache read and forces recomputation.
            return_metrics: If True, returns a tuple of (result_dict, VisualizationMetrics).

        Returns:
            Dictionary containing the serialized visualization graph,
            or a tuple of (serialized_dict, VisualizationMetrics) if return_metrics is True.

        Raises:
            TransformationStageError: If transformation fails.
            LayoutStageError: If layout computation fails.
            SerializationStageError: If serialization fails.
            CacheError: If cache read/write operations fail.
            VisualizationPipelineError: For other general pipeline failures.
        """
        if graph is None:
            raise TransformationStageError("RepositoryGraph input cannot be None.")

        # Check Cache if enabled and not forced
        cache_key = None
        if self.cache is not None:
            try:
                cache_key = generate_graph_cache_key(graph)
                if not force_compute:
                    cached_val = self.cache.get(cache_key)
                    if cached_val is not None:
                        # Cache Hit!
                        if return_metrics:
                            # Extract node/edge count from cached metadata if present
                            metadata = cached_val.get("metadata", {})
                            node_count = metadata.get("node_count", 0)
                            edge_count = metadata.get("edge_count", 0)
                            metrics = VisualizationMetrics(
                                node_count=node_count,
                                edge_count=edge_count,
                                cache_hit=True,
                                cache_miss=False,
                            )
                            return cached_val, metrics
                        return cached_val
            except CacheError:
                raise
            except Exception as err:
                raise CacheError(f"Cache retrieval failed: {err}") from err

        # Cache Miss or Cache Disabled or forced recomputation
        profiler = self.profiler or VisualizationProfiler(enabled=False)
        profiler.start("total")

        # 1. Transform Stage
        profiler.start("transformation")
        try:
            viz_graph = self.transformer.transform(graph)
        except TransformationError as err:
            raise TransformationStageError(f"Transformation stage failed: {err}") from err
        except Exception as err:
            raise TransformationStageError(f"Unexpected error in transformation stage: {err}") from err
        transformation_time = profiler.stop("transformation")

        # 2. Layout Stage
        profiler.start("layout")
        try:
            positioned_graph = self.layout_engine.layout(viz_graph)
        except LayoutEngineError as err:
            raise LayoutStageError(f"Layout stage failed: {err}") from err
        except Exception as err:
            raise LayoutStageError(f"Unexpected error in layout stage: {err}") from err
        layout_time = profiler.stop("layout")

        # 3. Serialization Stage
        profiler.start("serialization")
        try:
            serialized_dict = self.serializer.to_dict(positioned_graph)
        except SerializationError as err:
            raise SerializationStageError(f"Serialization stage failed: {err}") from err
        except Exception as err:
            raise SerializationStageError(f"Unexpected error in serialization stage: {err}") from err
        serialization_time = profiler.stop("serialization")

        total_time = profiler.stop("total")

        # Save to Cache if enabled
        if self.cache is not None and cache_key is not None:
            try:
                self.cache.set(cache_key, serialized_dict)
            except Exception as err:
                raise CacheError(f"Cache write failed: {err}") from err

        if return_metrics:
            metrics = VisualizationMetrics(
                transformation_time_ms=transformation_time,
                layout_time_ms=layout_time,
                serialization_time_ms=serialization_time,
                total_time_ms=total_time,
                node_count=len(positioned_graph.nodes),
                edge_count=len(positioned_graph.edges),
                cache_hit=False,
                cache_miss=self.cache is not None,
            )
            return serialized_dict, metrics

        return serialized_dict
