import unittest
from ..accumulations import select_topmost_click_in_searches


class TestClickMetrics(unittest.TestCase):

    def test_returns_accumulations_with_topmost_click(self):
        accumulations = {}
        session_description = (
            "session1",
            {
                "search1": [("documentvieweropened", "qt-1-1"), ("documentviewed", "qt-1-2")],
                "search2": [("documentvieweropened", "re-2-10")],
            },
        )
        result = select_topmost_click_in_searches(accumulations, session_description)
        self.assertEqual({"session1": {"search1": 1, "search2": 2}}, result)

    def test_handles_no_click_events(self):
        accumulations = {}
        session_description = (
            "session2",
            {
                "search1": [("documentvieweropened", None), ("documentviewed", "")],
                "search2": [],
            },
        )
        result = select_topmost_click_in_searches(accumulations, session_description)
        self.assertEqual({"session2": {"search1": 9999, "search2": 9999}}, result)

    def test_ignores_invalid_event_tuples(self):
        accumulations = {}
        session_description = (
            "session3",
            {
                "search1": [("invalid_event", "qt-1-1"), "not_a_tuple"],
                "search2": [("documentvieweropened", "qt-1-5")],
            },
        )
        result = select_topmost_click_in_searches(accumulations, session_description)
        self.assertEqual({"session3": {"search1": 9999, "search2": 1}}, result)

    def test_handles_empty_session_description(self):
        accumulations = {}
        session_description = ("session4", {})
        result = select_topmost_click_in_searches(accumulations, session_description)
        self.assertEqual({}, result)

    def test_skips_non_tuple_session_description(self):
        accumulations = {}
        session_description = ["session5", {"search1": [("documentvieweropened", "qt-1-1")]}]
        result = select_topmost_click_in_searches(accumulations, session_description)
        self.assertEqual({}, result)