import unittest

from ..accumulations import collect_search_counts_in_sessions, collect_opened_links_in_searches
from ..accumulations import collect_opened_links_by_searchnumbers_in_session
from ..accumulations import collect_opened_documents_positions_distribution_in_searches
from ..accumulations import collect_opened_documents_positions_distribution_in_searches_v2
from ..accumulations import preprocess_events
from ..analyser import summarize_events


class TestSessionAnalytics(unittest.TestCase):

    session_description6 = ('00110346812',
                            {'0 8305769001 2680939': [('query', 'qt', 'mil'),
                                                      ('query', 'qt', 'mil-f'),
                                                      ('query', 'qt', 'mi'),
                                                      ('query', 'qt', 'mil-f-5'),
                                                      ('query', 'qt', 'mil-f-550'),
                                                      ('query', 'qt', 'mil-f-5509'),
                                                      ('query', 'qt', 'AS'),
                                                      ('query', 'qt', 'AS484'),
                                                      ('query', 'qt', 'AS4843'),
                                                      ('query', 'qt', 'AS48'),
                                                      ('query', 'qt', 'AS4'),
                                                      ('query', 'qt', 'AS487'),
                                                      ('query', 'qt', 'AS4875'),
                                                      ('query', 'qt', 'AS487'),
                                                      ('documentvieweropened', 'dv-dl', 'None'),
                                                      ('documentviewed', 'dv-dl', 'None')],
                             '6388 8305769001 2680939': [('query', 're', 'mil-f-5509')],
                             '6389 8305769001 2680939': [('query', 're', 'AS4843'),
                                                         ('documentvieweropened', 're-2-50', 'None'),
                                                         ('documentviewed', 're-2-50', 'None')],
                             '6381 8305769001 2680939': [('query', 're', 'AS4875'),
                                                         ('documentvieweropened', 're-4-50', 'None'),
                                                         ('documentviewed', 're-4-50', 'None')],
                             '6382 8305769001 2680939': [('query', 're', 'AS4843'),
                                                         ('documentvieweropened', 're-4-50', 'None'),
                                                         ('documentviewed', 're-4-50', 'None')]
                             }
                            )

    session_description7 = ('00110346812',
                            {'0 5940240053 2650302':
                                 [('query', 'qt', 'NACE AMPP MR0175; Errata: June 1, 2023; Errata: February 25, 2025'),
                                  ('query', 'qt', 'NACE AMPP MR01752; Errata: June 1, 2023; Errata: February 25, 2025'),
                                  ('query', 'qt', 'NACE AMPP MR017'),
                                  ('query', 'qt', 'NACE AMPP MR0175'),
                                  ('query', 'qt', 'NACE AMPP MR01'),
                                  ('query', 'qt', 'NACE AMPP MR0'),
                                  ('query', 'qt', 'NACE AMPP MR010'),
                                  ('query', 'qt', 'NACE AMPP MR01'),
                                  ('query', 'qt', 'NACE AMPP MR0103'),
                                  ('documentvieweropened', 'qt-1-8', 'None'),
                                  ('documentviewed', 'qt-1-8', 'None')],
                             '638896281191559154 5940240053 2650302':
                                 [('query', 're', 'NACE AMPP MR0103 - Petroleum, petrochemical and natural gas industries - Metallic materials resistant to sulfide stress cracking in corrosive petroleum refining environments')
                                  ]
                             }
                            )



    session_description9 = ('00363979599',
                            {'0 8353308001 335781':
                                 [('query', 'qt', '41'),
                                  ('query', 'qt', '4100'),
                                  ('query', 'qt', '410'),
                                  ('documentvieweropened', 'qt-1-8', 'None'),
                                  ('documentviewed', 'qt-1-8', 'None'),
                                  ('query', 'qt', '3600'),
                                  ('query', 'qt', '3'),
                                  ('query', 'qt', '360'),
                                  ('query', 'qt', '36'),
                                  ('documentvieweropened', 'qt-1-8', 'None'),
                                  ('documentviewed', 'qt-1-8', 'None'),
                                  ('query', 'qt', '510'),
                                  ('query', 'qt', '51'),
                                  ('query', 'qt', '5100'),
                                  ('query', 'qt', '5'),
                                  ('query', 'qt', '5100.5'),
                                  ('query', 'qt', '5100.'),
                                  ('documentvieweropened', 'qt-1-8', 'None'),
                                  ('documentviewed', 'qt-1-8', 'None')],
                             '638896035403180314 8353308001 335781':
                                 [('query', 're', 'SA AS 4100 - Steel structures - Third Edition; Incorporating Amendment No. 1: 9/2021')],
                             '638896036945704568 8353308001 335781':
                                 [('query', 're', 'SA AS 3600 - Concrete structures - Fifth Edition; Incorporating Amendment No. 1: 11/2018; Incorporating Amendment No. 2: 5/2021')],
                             '638896203898549852 8353308001 335781':
                                 [('query', 're', 'SA AS 5100.5 - Bridge design, Part 5: Concrete - Second Edition; Incorporating Amendment No 1: 11/2018; Amendment No 2: 5/2024')]
                             }
                            )

    session_descriptionA = ('00363979599',
                            {
                                '638896035403180314 8353308001 335781':
                                    [('query', 're',
                                      'SA AS 4100 - Steel structures - Third Edition; Incorporating  No. 1: 9/2021')],
                                '638896036945704568 8353308001 335781':
                                    [('query', 're',
                                      'SA AS 3600 - Concrete structures - Edition Incorporating No.11/2018; No. 5/20')],
                                '638896203898549852 8353308001 335781':
                                    [('query', 're',
                                      'SA AS 5100.5 - Bridge design, Part 5: Concrete - Second Edition; No 2: 5/2024')]
                             }
                            )

    session_descriptionB = ('00363979599',
                            {'0 8353308001 335781':
                                 [('query', 'qt', '41'),
                                  ('query', 'qt', '4100'),
                                  ('query', 'qt', '410'),
                                  ('documentvieweropened', 'qt-1-8', 'None'),
                                  ('documentviewed', 'qt-1-8', 'None'),
                                  ('query', 'qt', '3600'),
                                  ('query', 'qt', '3'),
                                  ('query', 'qt', '360'),
                                  ('query', 'qt', '36'),
                                  ('documentvieweropened', 'qt-2-8', 'None'),
                                  ('documentviewed', 'qt-2-8', 'None'),
                                  ('query', 'qt', '510'),
                                  ('query', 'qt', '51'),
                                  ('query', 'qt', '5100'),
                                  ('query', 'qt', '5'),
                                  ('query', 'qt', '5100.5'),
                                  ('query', 'qt', '5100.'),
                                  ('documentvieweropened', 'qt-3-8', 'None'),
                                  ('documentviewed', 'qt-3-8', 'None')]
                             }
                            )

    session_descriptionC = ('00500722015',
                            {'0 5913259001 2567696':
                                [('documentvieweropened', 'qt-1-8', 'None'),
                                 ('documentviewed', 'qt-1-8', 'None')],
                             '638869259347934788 5913259001 2567696':
                                 [('query', 're', 'ICC I-CODE IMC - I-Codes: IMC - International Mechanical Code')]
                             }
                            )




    def test_collect_opened_links_in_searches(self):
        counts = {}
        counts = collect_opened_links_in_searches(counts, self.session_description6)
        self.assertEqual({0: 5}, counts)

    def test_distribution_emptyQTA(self):
        counts = {}
        counts = preprocess_events(counts, self.session_descriptionA)
        res = summarize_events(counts, collect_opened_documents_positions_distribution_in_searches_v2)
        self.assertEqual({3: {'0': 3}}, res)

    def test_distribution_onlyQTA(self):
        counts = {}
        counts = preprocess_events(counts, self.session_descriptionB)
        res = summarize_events(counts, collect_opened_documents_positions_distribution_in_searches_v2)
        self.assertEqual({1: {'1': 1, '2': 1, '3': 1}}, res)

    def test_collects_search_countsC(self):
        counts = {}
        counts = preprocess_events(counts, self.session_descriptionC)
        res = summarize_events(counts, collect_opened_documents_positions_distribution_in_searches_v2)
        self.assertEqual({1: {'1': 1}}, res)

    def test_collects_search_counts6(self):
        counts = {}
        counts = preprocess_events(counts, self.session_description6)
        res = summarize_events(counts, collect_opened_documents_positions_distribution_in_searches_v2)
        self.assertEqual({1: {'1': 1}}, res)

    def test_collects_search_counts9(self):
        counts = {}
        counts = preprocess_events(counts, self.session_description9)
        res = summarize_events(counts, collect_opened_documents_positions_distribution_in_searches_v2)
        self.assertEqual({3: {'1': 3}}, res)
