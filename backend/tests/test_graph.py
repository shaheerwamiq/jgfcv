"""Graph structure tests — verify wiring without LLM calls."""

from src.agents.graph import build_graph, route_to_agent


class TestRouting:
    def test_route_reads_state(self):
        assert route_to_agent({"route": "research"}) == "research"
        assert route_to_agent({"route": "analyst"}) == "analyst"
        assert route_to_agent({"route": "writer"}) == "writer"

    def test_route_defaults_to_writer(self):
        assert route_to_agent({}) == "writer"


class TestGraphStructure:
    def test_graph_compiles(self):
        app = build_graph()
        assert app is not None

    def test_graph_has_all_nodes(self):
        app = build_graph()
        nodes = set(app.get_graph().nodes.keys())
        assert {"supervisor", "research", "analyst", "writer"} <= nodes

    def test_supervisor_is_entry(self):
        app = build_graph()
        graph = app.get_graph()
        starts = {e.target for e in graph.edges if e.source == "__start__"}
        assert starts == {"supervisor"}
