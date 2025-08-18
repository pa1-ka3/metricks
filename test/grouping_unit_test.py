import unittest

class TestSessionAnalytics(unittest.TestCase):


    session_description6 = {'0 8305769001 2680939': [('query', 'qt', 'mil'),
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

    session_description7 = {'0 5940240053 2650302':
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
                                 ]}