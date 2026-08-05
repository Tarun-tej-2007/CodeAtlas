"""Unit tests for the Dashboard Aggregation Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.dashboard import (
    DashboardValidationError,
    DashboardWidgetType,
    DashboardStatus,
    DashboardModel,
    DashboardView,
    DashboardWidgetRegistry,
    DashboardAggregationEngine,
)


class DummyWidgetView(DashboardView):
    """Widget view with customizable attributes for aggregation tests."""

    def __init__(self, widget_type: DashboardWidgetType, title: str, return_val: str) -> None:
        self.widget_type = widget_type
        self.title = title
        self.return_val = return_val

    def render(self, context: Any) -> str:
        # Context is forwarded unchanged
        return f"{self.return_val} - Context: {context}"


class FailingWidgetView(DashboardView):
    """Widget view that throws during execute/render."""

    def render(self, context: Any) -> Any:
        raise ValueError("Widget execution error")


class TestDashboardEngine(unittest.TestCase):
    """Verifies widget mapping, context propagation, error bubbling, metadata collection, and concurrent runs."""

    def setUp(self) -> None:
        self.registry = DashboardWidgetRegistry()
        self.engine = DashboardAggregationEngine(self.registry)
        self.context = {"metrics": [10, 20]}

    def test_constructor_validation(self) -> None:
        """Verifies engine construction rejects invalid dependencies."""
        with self.assertRaises(ValueError):
            DashboardAggregationEngine(None)  # type: ignore

        with self.assertRaises(TypeError):
            DashboardAggregationEngine("not_a_registry")  # type: ignore

    def test_empty_registry_aggregation(self) -> None:
        """Verifies aggregation works when no widgets are registered, compiling empty dashboard DTO."""
        res = self.engine.compile(project_name="EmptyProj", context=self.context)
        self.assertEqual(res.metadata.project_name, "EmptyProj")
        self.assertEqual(res.metadata.status, DashboardStatus.READY)
        self.assertEqual(len(res.widgets), 0)
        self.assertEqual(len(res.metadata.extra_info), 0)

    def test_single_and_multiple_widget_aggregation(self) -> None:
        """Verifies mapping of known widget types and context forwarding."""
        w1 = DummyWidgetView(DashboardWidgetType.SUMMARY, "Summary Widget", "SummaryData")
        w2 = DummyWidgetView(DashboardWidgetType.METRICS, "Metrics Widget", "MetricsData")

        self.registry.register("w1", w1)
        self.registry.register("w2", w2)

        res = self.engine.compile(project_name="MultiProj", context="MyContext")

        self.assertEqual(res.metadata.project_name, "MultiProj")
        self.assertEqual(len(res.widgets), 2)
        self.assertIn("summary", res.widgets)
        self.assertIn("metrics", res.widgets)

        self.assertEqual(res.widgets["summary"].content, "SummaryData - Context: MyContext")
        self.assertEqual(res.widgets["metrics"].content, "MetricsData - Context: MyContext")

    def test_custom_widget_metadata_aggregation(self) -> None:
        """Verifies unknown or custom widget types are routed to metadata extra_info."""
        custom_widget = DummyWidgetView("custom_type", "Custom Widget", "CustomData")  # type: ignore
        self.registry.register("my_custom_widget", custom_widget)

        res = self.engine.compile(project_name="CustomProj", context="CustomContext")

        self.assertEqual(len(res.widgets), 0)
        self.assertIn("my_custom_widget", res.metadata.extra_info)
        self.assertEqual(
            res.metadata.extra_info["my_custom_widget"],
            "CustomData - Context: CustomContext",
        )

    def test_exception_propagation(self) -> None:
        """Verifies widget execution exceptions bubble up directly and are not swallowed."""
        self.registry.register("failing", FailingWidgetView())

        with self.assertRaises(ValueError) as ctx:
            self.engine.compile(project_name="ErrorProj", context=self.context)
        self.assertEqual(str(ctx.exception), "Widget execution error")

    def test_render_view_contract(self) -> None:
        """Verifies that the render contract returns the dashboard model successfully."""
        dashboard = self.engine.compile(project_name="RenderProj", context=self.context)
        rendered = self.engine.render(dashboard)
        self.assertEqual(rendered, dashboard)

        with self.assertRaises(DashboardValidationError):
            self.engine.render(None)  # type: ignore

        with self.assertRaises(TypeError):
            self.engine.render("not_a_dashboard")  # type: ignore

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent compilation runs."""
        w1 = DummyWidgetView(DashboardWidgetType.SUMMARY, "Summary Widget", "SummaryData")
        self.registry.register("w1", w1)

        def compile_task(index: int):
            return self.engine.compile(project_name=f"Proj_{index}", context=self.context)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(compile_task, i) for i in range(25)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertIn("summary", res.widgets)
            self.assertEqual(res.metadata.status, DashboardStatus.READY)


if __name__ == "__main__":
    unittest.main()
