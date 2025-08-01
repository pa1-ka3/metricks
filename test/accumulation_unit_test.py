from ..accumulations import collect_search_counts_in_sessions, collect_opened_links_in_searches
from ..accumulations import collect_opened_links_by_searchnumbers_in_session
from ..accumulations import collect_opened_documents_positions_distribution_in_searches

import unittest


class TestSessionAnalytics(unittest.TestCase):

    def test_collects_search_counts_correctly(self):
        counts = {}
        session_description = ("session1", ["search1", "search2", "search3"])
        result = collect_search_counts_in_sessions(counts, session_description)
        self.assertEqual(result, {3: 1})

    def test_updates_existing_search_counts(self):
        counts = {3: 2}
        session_description = ("session2", ["search1", "search2", "search3"])
        result = collect_search_counts_in_sessions(counts, session_description)
        self.assertEqual(result, {3: 3})

    def test_handles_non_tuple_session_description_for_search_counts(self):
        counts = {}
        session_description = {"invalid": "data"}
        result = collect_search_counts_in_sessions(counts, session_description)
        self.assertEqual(result, {})

    def test_collects_opened_links_correctly(self):
        counts = {}
        session_description = ("session1", {
            "query1": ["documentvieweropened1", "documentviewed2", "downloadpdf3"],
            "query2": ["documentvieweropened1", "documentviewed2"]
        })
        result = collect_opened_links_in_searches(counts, session_description)
        self.assertEqual(result, {3: 1, 2: 1})

    def test_updates_existing_opened_links_counts(self):
        counts = {3: 1}
        session_description = ("session2", {
            "query1": ["documentvieweropened1", "documentviewed2", "downloadpdf3"]
        })
        result = collect_opened_links_in_searches(counts, session_description)
        self.assertEqual(result, {3: 2})

    def test_handles_non_tuple_session_description_for_opened_links(self):
        counts = {}
        session_description = {"invalid": "data"}
        result = collect_opened_links_in_searches(counts, session_description)
        self.assertEqual(result, {})


class TestIntegration(unittest.TestCase):
    session_description1 = ('00002619125', {638819595913961392: ['query re'], 638819640077367736: ['query re'],
                                            638819640427092704: ['query re'], 638819640639623962: ['query re'],
                                            638819650426382636: ['query re']})

    session_description2 = ('00542416250', {638819639956585652: ['query re'],
                                            0: ['documentviewed qt-1-8',
                                                'documentvieweropened qt-1-8',
                                                'downloadpdf None']})

    session_description3 = ('00517727087', {638819648035451543: ['documentvieweropened as-30-10',
                                                                 'documentviewed as-30-10', 'query as',
                                                                 'documentvieweropened as-1-10',
                                                                 'documentviewed as-1-10',
                                                                 'documentvieweropened as-3-10',
                                                                 'documentviewed as-3-10'],
                                            638819649075469465: ['documentvieweropened as-31-10',
                                                                 'documentviewed as-31-10', 'downloadpdf None']})

    session_description4 = ('00517727087', {638819648035451543: ['documentvieweropened as-3-10',
                                                                 'documentviewed as-3-10', 'query as']})

    session_description5 = ('00517727087', {638819648035451543: ['query re', 'downloadpdf None']})

    def test_collects_search_counts(self):
        counts = {}
        counts = collect_search_counts_in_sessions(counts, self.session_description1)
        self.assertEqual({5: 1}, counts)

        # simulate analyse next session
        counts = collect_search_counts_in_sessions(counts, self.session_description2)
        self.assertEqual({2: 1, 5: 1}, counts)

        # simulate analyse one more session
        counts = collect_search_counts_in_sessions(counts, self.session_description3)
        self.assertEqual({2: 2, 5: 1}, counts)

        counts = collect_search_counts_in_sessions(counts, self.session_description4)
        self.assertEqual({1: 1, 2: 2, 5: 1}, counts)

        counts = collect_search_counts_in_sessions(counts, self.session_description5)
        self.assertEqual({1: 2, 2: 2, 5: 1}, counts)

    def test_collect_opened_links_in_searches(self):
        counts = {}
        counts = collect_opened_links_in_searches(counts, self.session_description1)
        self.assertEqual({0: 5}, counts)

        counts = collect_opened_links_in_searches(counts, self.session_description2)
        self.assertEqual({0: 6, 1: 1}, counts)

        counts = collect_opened_links_in_searches(counts, self.session_description3)
        self.assertEqual({0: 6, 1: 2, 3: 1}, counts)

        counts = collect_opened_links_in_searches(counts, self.session_description4)
        self.assertEqual({0: 6, 1: 3, 3: 1}, counts)

        counts = collect_opened_links_in_searches(counts, self.session_description5)
        self.assertEqual({0: 6, 1: 4, 3: 1}, counts)

    def test_collect_opened_links_in_searches5(self):
        counts = {}
        counts = collect_opened_links_in_searches(counts, self.session_description5)
        self.assertEqual({1: 1}, counts)

    def test_collect_opened_links_by_searchnumbers_in_session(self):
        counts = {}
        counts = collect_opened_links_by_searchnumbers_in_session(counts, self.session_description1)
        self.assertEqual({5: {0: 5}}, counts)

        counts = collect_opened_links_by_searchnumbers_in_session(counts, self.session_description2)
        self.assertEqual({5: {0: 5}, 2: {0: 1, 1: 1}}, counts)

        counts = collect_opened_links_by_searchnumbers_in_session(counts, self.session_description3)
        self.assertEqual({5: {0: 5}, 2: {0: 1, 1: 2, 3: 1}}, counts)

    def test_collect_opened_documents_positions_distribution_in_searches(self):
        counts = {}
        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description2)
        self.assertEqual({2: {'downloadpdf': 1, '0': 1, '1': 1}}, counts)

        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description1)
        self.assertEqual({2: {'downloadpdf': 1, '0': 1, '1': 1}, 5: {'0': 5}}, counts)

        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description3)
        self.assertEqual({2: {'downloadpdf': 2, '0': 1, '1': 2, '3': 1, '(21-100)': 2}, 5: {'0': 5}}, counts)

    def test_only_re(self):
        counts = {}
        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description1)
        self.assertEqual({5: {'0': 5}}, counts)

    def test_only_re3(self):
        counts = {}
        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description3)
        self.assertEqual({2: {'downloadpdf': 1, '1': 1, '3': 1, '(21-100)': 2}}, counts)

    def test_extra_re_in_searches(self):
        counts = {}
        counts = collect_opened_documents_positions_distribution_in_searches(counts, self.session_description4)
        self.assertEqual({1: {'3': 1}}, counts)


class TestSearchNumbersInSearches(unittest.TestCase):
    def collects_opened_links_by_searchnumbers_correctly(self):
        counts = {}
        session_description = ("session1", {
            "query1": ["documentvieweropened1", "documentviewed2", "downloadpdf3"],
            "query2": ["documentvieweropened4", "documentviewed5"]
        })
        result = collect_opened_links_by_searchnumbers_in_session(counts, session_description)
        self.assertEqual(result, {2: {3: 1, 2: 1}})

    def handles_non_tuple_session_description_for_opened_links_by_searchnumbers(self):
        counts = {}
        session_description = {"invalid": "data"}
        result = collect_opened_links_by_searchnumbers_in_session(counts, session_description)
        self.assertEqual(result, {})

    def test_handles_empty_session_description_for_opened_links_by_searchnumbers(self):
        counts = {}
        session_description = ('00628800572', {638822006652765274: ['query re']})
        # session_description = ("session1", {})

        result = collect_opened_links_by_searchnumbers_in_session(counts, session_description)
        self.assertEqual({1: {0: 1}}, result)
