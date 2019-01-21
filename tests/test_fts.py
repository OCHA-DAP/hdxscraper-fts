#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Unit tests for fts.

'''
from datetime import datetime
from os.path import join

import pytest
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country
from hdx.utilities.compare import assert_files_same
from hdx.utilities.downloader import DownloadError
from hdx.utilities.path import temp_dir

from fts import generate_dataset_and_showcase, get_countries


class TestFTS:    
    countries = [{
        'id': 1,
        'iso3': 'AFG',
        'name': 'Afghanistan'
    }, {
        'id': 3,
        'iso3': 'ALB',
        'name': 'Albania'
    }, {
        'id': 41,
        'iso3': 'CPV',
        'name': 'Cape Verde'}
    ]

    afgflows = [{'firstReportedDate': '2016-11-09T00:00:00Z', 'contributionType': 'financial',
              'createdAt': '2017-05-15T15:20:52.142Z', 'budgetYear': '2016', 'date': '2017-04-17T00:00:00Z',
              'childFlowIds': None, 'amountUSD': 10250000, 'method': 'Traditional aid', 'exchangeRate': None,
              'updatedAt': '2017-05-15T15:20:52.142Z', 'keywords': ['USA/BPRM'],
              'sourceObjects': [{'type': 'Organization',  'id': '2933', 'name': 'United States of America, Government of',
                                 'organizationTypes': ['Government', 'National government']},
                                {'type': 'Location', 'id': '237', 'name': 'United States'}, {'type': 'Location', 'id': '237', 'name': 'Bermuda'},
                                {'type': 'UsageYear', 'id': '38', 'name': '2017'}], 'refCode': 'FS # 2 FY 2017',
                 'destinationObjects': [{'type': 'Organization', 'id': '2967', 'name': 'International Committee of the Red Cross',
                                     'organizationTypes': ['Red Cross/Red Crescent']},
                                     {'type': 'Plan', 'id': '544', 'name': 'Afghanistan 2017', 'behavior': 'single'},
                                     {'type': 'GlobalCluster', 'id': '4', 'name': 'Emergency Shelter and NFI', 'behavior': 'single'},
                                     {'type': 'GlobalCluster', 'id': '11', 'name': 'Water Sanitation Hygiene', 'behavior': 'single'},
                                     {'type': 'Location', 'id': '1', 'name': 'Afghanistan'},
                                     {'type': 'Project', 'id': '54621', 'name': 'Cholera and other water borne diseases Shield WASH Project', 'behavior': 'single', 'code': 'HTI-18/WS/125105/124'},
                                     {'type': 'UsageYear', 'id': '38', 'name': '2018'}, {'type': 'UsageYear', 'id': '38', 'name': '2017'}], 'flowType': 'Standard',
                 'reportDetails': [{'date': '2017-04-18T00:00:00.000Z',
                                 'organization': 'United States of America, Government of', 'sourceType': 'Primary',
                                 'reportChannel': 'Email'}], 'parentFlowId': None, 'originalCurrency': 'USD',
                 'status': 'commitment', 'id': '149198', 'boundary': 'incoming',
                 'description': 'Humanitarian Assistance (STATE/PRM)', 'decisionDate': '2016-06-24T00:00:00Z',
                 'versionId': 2}]

    cpvflows = [{'id': '170870', 'versionId': 1, 'description': 'The project will help restore, protect livelihoods and increase the resilience of households affected by drought in Cabo Verde.',
                 'status': 'paid', 'date': '2018-02-16T00:00:00Z', 'amountUSD': 218918, 'exchangeRate': None, 'firstReportedDate': '2018-02-16T00:00:00Z', 'budgetYear': None,
                 'decisionDate': '2018-02-16T00:00:00Z', 'flowType': 'Standard', 'contributionType': 'financial', 'keywords': None, 'method': 'Traditional aid', 'parentFlowId': None, 'childFlowIds': None,
                 'newMoney': True, 'createdAt': '2018-02-20T13:09:45.158Z', 'updatedAt': '2018-02-20T13:09:45.158Z',
                 'sourceObjects': [{'type': 'Organization', 'id': '2927', 'name': 'Belgium, Government of', 'behavior': 'single', 'organizationTypes': ['Government'], 'organizationSubTypes': ['National government']},
                                   {'type': 'Location', 'id': '22', 'name': 'Belgium', 'behavior': 'single'},
                                   {'type': 'UsageYear', 'id': '39', 'name': '2018', 'behavior': 'single'}],
                 'destinationObjects': [{'type': 'Organization', 'id': '4399', 'name': 'Food & Agriculture Organization of the United Nations',
                                         'behavior': 'single', 'organizationTypes': ['UN agency']}, {'type': 'GlobalCluster', 'id': '26512', 'name': 'Agriculture', 'behavior': 'single'},
                                        {'type': 'Location', 'id': '41', 'name': 'Cape Verde', 'behavior': 'single'}, {'type': 'UsageYear', 'id': '39', 'name': '2018', 'behavior': 'single'}],
                 'boundary': 'incoming', 'onBoundary': 'single', 'reportDetails': [{'sourceType': 'Primary', 'organization': 'Food & Agriculture Organization of the United Nations',
                                                                                    'reportChannel': 'FTS Web', 'date': '2018-02-16T00:00:00.000Z'}], 'refCode': 'OSRO/CVI/802/BEL'}]

    albflows = [{'id': '174423', 'versionId': 1, 'description': 'Provision of 1,000 food parcels to the most needed people in Albania via Muslim Community of Albania',
                 'status': 'paid', 'date': '2018-02-15T00:00:00Z', 'amountUSD': 86754, 'originalAmount': 325328, 'originalCurrency': 'SAR', 'exchangeRate': 3.75, 'firstReportedDate': '2018-05-02T00:00:00Z',
                 'budgetYear': None, 'decisionDate': None, 'flowType': 'Standard', 'contributionType': 'financial', 'keywords': None, 'method': 'Traditional aid', 'parentFlowId': None, 'childFlowIds': None,
                 'newMoney': True, 'createdAt': '2018-05-14T09:55:20.374Z', 'updatedAt': '2018-05-14T09:55:20.374Z',
                 'sourceObjects': [{'type': 'Organization', 'id': '2998', 'name': 'Saudi Arabia (Kingdom of), Government of', 'behavior': 'single', 'organizationTypes': ['Government'], 'organizationSubTypes': ['National government']},
                                   {'type': 'Location', 'id': '196', 'name': 'Saudi Arabia', 'behavior': 'single'},
                                   {'type': 'UsageYear', 'id': '39', 'name': '2018', 'behavior': 'single'}],
                 'destinationObjects': [{'type': 'Cluster', 'id': '4206', 'name': 'Food security', 'behavior': 'single'},
                                        {'type': 'GlobalCluster', 'id': '6', 'name': 'Food Security', 'behavior': 'single'},
                                        {'type': 'Location', 'id': '3', 'name': 'Albania', 'behavior': 'single'},
                                        {'type': 'UsageYear', 'id': '39', 'name': '2018', 'behavior': 'single'}],
                 'boundary': 'incoming', 'onBoundary': 'single', 'reportDetails': [{'sourceType': 'Primary', 'organization': 'Saudi Arabia (Kingdom of), Government of',
                                                                                    'reportChannel': 'Email', 'date': '2018-05-02T00:00:00.000Z'}], 'refCode': '291'}]

    afgrequirements = [{'locations': [{'iso3': 'AFG', 'id': 1, 'name': 'Afghanistan', 'adminLevel': 0}], 'id': 645,
                     'emergencies': [], 'code': 'HAFG18', 'years': [{'id': 39, 'year': '2018'}],
                     'startDate': '2018-01-01T00:00:00.000Z', 'endDate': '2018-12-31T00:00:00.000Z',
                     'name': 'Afghanistan 2018',
                     'categories': [{'id': 4, 'name': 'Humanitarian response plan', 'group': 'planType', 'code': None}],
                     'revisedRequirements': 437000000},
                       {'locations': [{'iso3': 'AFG', 'id': 1, 'name': 'Afghanistan', 'adminLevel': 0}], 'id': 544,
                     'emergencies': [], 'code': 'HAFG17', 'years': [{'id': 38, 'year': '2017'}],
                     'startDate': '2017-01-01T00:00:00.000Z', 'endDate': '2017-12-31T00:00:00.000Z',
                     'name': 'Afghanistan 2017',
                     'categories': [{'id': 4, 'name': 'Humanitarian response plan', 'group': 'planType', 'code': None}],
                     'revisedRequirements': 409413812}]

    cpvrequirements = [{'id': 222, 'name': 'West Africa 2007', 'code': 'CXWAF07', 'startDate': '2007-01-01T00:00:00.000Z',
                         'endDate': '2007-12-31T00:00:00.000Z', 'currentReportingPeriodId': None, 'isForHPCProjects': False,
                         'locations': [{'id': 41, 'iso3': 'CPV', 'name': 'Cape Verde', 'adminLevel': 0}], 'emergencies': [], 'years': [{'id': 28, 'year': '2007'}],
                         'categories': [{'id': 110, 'name': 'CAP', 'group': 'planType', 'code': None}], 'origRequirements': 309081675, 'revisedRequirements': 361026890}]

    afgobjectsBreakdown = [{'sharedFunding': 0, 'onBoundaryFunding': 0, 'direction': 'destination',
                         'totalFunding': 2500000, 'name': 'Afghanistan 2018', 'overlapFunding': 0, 'id': '645',
                         'singleFunding': 2500000, 'type': 'Plan'},
                           {'sharedFunding': 0, 'onBoundaryFunding': 1489197, 'direction': 'destination',
                         'totalFunding': 318052952, 'name': 'Afghanistan 2017', 'overlapFunding': 0, 'id': '544',
                         'singleFunding': 318052952, 'type': 'Plan'},
                           {'sharedFunding': '', 'onBoundaryFunding': 3391, 'direction': '',
                        'totalFunding': 3121940000, 'name': 'Not specified', 'overlapFunding': '', 'id': '',
                        'singleFunding': '', 'type': 'Plan'}]

    cpvobjectsBreakdown = [{'type': 'Plan', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': 16922064,
                            'singleFunding': 16922064, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    albobjectsBreakdown = [{'type': 'Plan', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': 20903498,
                            'singleFunding': 20903498, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0},
                           {'type': 'Plan', 'direction': 'destination', 'id': '90', 'name': 'Southeastern Europe 2002',
                            'totalFunding': 470201, 'singleFunding': 470201, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    objectsBreakdownnoid = [{'sharedFunding': '', 'onBoundaryFunding': 3391, 'direction': '',
                             'totalFunding': 3121940000, 'name': 'Not specified', 'overlapFunding': '',
                             'singleFunding': '', 'type': 'Plan'}]

    afgcluster_objectsBreakdown = [{'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Protection', 'id': '10', 'totalFunding': 12152422, 'singleFunding': 12152422, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Emergency Shelter and NFI', 'id': '4', 'totalFunding': 33904754, 'singleFunding': 33904754, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Food Security', 'id': '6', 'totalFunding': 498462845, 'singleFunding': 498462845, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Education', 'id': '3', 'totalFunding': 65668317, 'singleFunding': 65668317, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Multi-sector', 'id': '26479', 'totalFunding': 317252284, 'singleFunding': 317252284, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Coordination and support services', 'id': '26480', 'totalFunding': 58076793, 'singleFunding': 58076793, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Health', 'id': '7', 'totalFunding': 76050805, 'singleFunding': 76050805, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Agriculture', 'id': '26512', 'totalFunding': 61347440, 'singleFunding': 61347440, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Mine Action', 'id': '15', 'totalFunding': 27771389, 'singleFunding': 27771389, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Water Sanitation Hygiene', 'id': '11', 'totalFunding': 11933249, 'singleFunding': 11933249, 'type': 'GlobalCluster', 'direction': 'destination'}, {'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0, 'name': 'Early Recovery', 'id': '2', 'totalFunding': 34073658, 'singleFunding': 34073658, 'type': 'GlobalCluster', 'direction': 'destination'}]

    cpvcluster_objectsBreakdown = [{'type': 'GlobalCluster', 'direction': 'destination', 'id': '10', 'name': 'Protection', 'totalFunding': 1876756, 'singleFunding': 1876756, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '26479', 'name': 'Multi-sector', 'totalFunding': 41590301, 'singleFunding': 41590301, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': -17722648, 'singleFunding': -17722648, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '6', 'name': 'Food Security', 'totalFunding': 143193602, 'singleFunding': 143193602, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '7', 'name': 'Health', 'totalFunding': 21925347, 'singleFunding': 21925347, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '26512', 'name': 'Agriculture', 'totalFunding': 5403364, 'singleFunding': 5403364, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '26480', 'name': 'Coordination and support services', 'totalFunding': 8478913, 'singleFunding': 8478913, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'GlobalCluster', 'direction': 'destination', 'id': '11', 'name': 'Water Sanitation Hygiene', 'totalFunding': 735967, 'singleFunding': 735967, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    albcluster_objectsBreakdown = [{'type': 'Cluster', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': 134665994, 'singleFunding': 134665994, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    afgcluster_objects = [{'revisedRequirements': 85670595, 'origRequirements': 85670595, 'name': 'Agriculture', 'id': 26512, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 64933280, 'origRequirements': 56933280, 'name': 'Coordination and support services', 'id': 26480, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 171088509, 'origRequirements': 171088509, 'name': 'Early Recovery', 'id': 2, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 96995379, 'origRequirements': 96995379, 'name': 'Education', 'id': 3, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 82751013, 'origRequirements': 82751013, 'name': 'Emergency Shelter and NFI', 'id': 4, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 591933076, 'origRequirements': 591933076, 'name': 'Food Security', 'id': 6, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 188971264, 'origRequirements': 188971264, 'name': 'Health', 'id': 7, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 49455000, 'origRequirements': 49455000, 'name': 'Mine Action', 'id': 15, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 381778683, 'origRequirements': 373163674, 'name': 'Multi-sector', 'id': 26479, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 25810653, 'origRequirements': 25810653, 'name': 'Protection', 'id': 10, 'objectType': 'GlobalCluster'}, {'revisedRequirements': 41122187, 'origRequirements': 41122187, 'name': 'Water Sanitation Hygiene', 'id': 11, 'objectType': 'GlobalCluster'}]

    cpvcluster_objects = [{'id': 26512, 'name': 'Agriculture', 'objectType': 'GlobalCluster', 'revisedRequirements': 26582420, 'origRequirements': 24926460}, {'id': 26480, 'name': 'Coordination and support services', 'objectType': 'GlobalCluster', 'revisedRequirements': 17763017, 'origRequirements': 13772460}, {'id': 6, 'name': 'Food Security', 'objectType': 'GlobalCluster', 'revisedRequirements': 173029390, 'origRequirements': 125026018}, {'id': 7, 'name': 'Health', 'objectType': 'GlobalCluster', 'revisedRequirements': 59740170, 'origRequirements': 38385069}, {'id': 15, 'name': 'Mine Action', 'objectType': 'GlobalCluster', 'revisedRequirements': 286125, 'origRequirements': 0}, {'id': 26479, 'name': 'Multi-sector', 'objectType': 'GlobalCluster', 'revisedRequirements': 63983519, 'origRequirements': 91596988}, {'id': 10, 'name': 'Protection', 'objectType': 'GlobalCluster', 'revisedRequirements': 17107095, 'origRequirements': 14035130}, {'id': 11, 'name': 'Water Sanitation Hygiene', 'objectType': 'GlobalCluster', 'revisedRequirements': 2001345, 'origRequirements': 1082750}, {'name': 'Not specified', 'objectType': 'GlobalCluster', 'revisedRequirements': 533809, 'origRequirements': 256800}]

    albcluster_objects = [{'name': 'Not specified', 'objectType': 'Cluster', 'revisedRequirements': 212686531, 'origRequirements': 236654801}]

    afg645location_objectsBreakdown = [{'type': 'Location', 'direction': 'destination', 'id': '1', 'name': 'Afghanistan', 'totalFunding': 462150015, 'singleFunding': 462150015, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    afg544location_objectsBreakdown = [{'type': 'Location', 'direction': 'destination', 'id': '1', 'name': 'Afghanistan', 'totalFunding': 331238992, 'singleFunding': 331238992, 'overlapFunding': 0, 'sharedFunding': 1489197, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '25799581', 'onBoundaryFunding': 0, 'name': 'Western', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799580', 'onBoundaryFunding': 0, 'name': 'Southern', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799579', 'onBoundaryFunding': 0, 'name': 'South Eastern', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799578', 'onBoundaryFunding': 0, 'name': 'Northern', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799574', 'onBoundaryFunding': 0, 'name': 'Central Highland', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799575', 'onBoundaryFunding': 0, 'name': 'Capital', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799576', 'onBoundaryFunding': 0, 'name': 'Eastern', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '25799577', 'onBoundaryFunding': 0, 'name': 'North Eastern', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 592979}, {'type': 'Location', 'direction': 'destination', 'id': '4060', 'onBoundaryFunding': 0, 'name': 'Capital', 'totalFunding': 0, 'singleFunding': 0, 'overlapFunding': 0, 'sharedFunding': 896218}]

    cpvlocation_objectsBreakdown = [{'type': 'Location', 'direction': 'destination', 'id': '93', 'name': 'Guinea', 'totalFunding': 19613744, 'singleFunding': 19613744, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': 69727905, 'singleFunding': 69727905, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '94', 'name': 'Guinea-Bissau', 'totalFunding': 7934188, 'singleFunding': 7934188, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '197', 'name': 'Senegal', 'totalFunding': 5385626, 'singleFunding': 5385626, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '81', 'name': 'Gambia', 'totalFunding': 85231, 'singleFunding': 85231, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '137', 'name': 'Mali', 'totalFunding': 9155718, 'singleFunding': 9155718, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '36', 'name': 'Burkina Faso', 'totalFunding': 10753570, 'singleFunding': 10753570, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '162', 'name': 'Niger', 'totalFunding': 20855001, 'singleFunding': 20855001, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '126', 'name': 'Liberia', 'totalFunding': 23638958, 'singleFunding': 23638958, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '141', 'name': 'Mauritania', 'totalFunding': 17446352, 'singleFunding': 17446352, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '224', 'name': 'Togo', 'totalFunding': 7893281, 'singleFunding': 7893281, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '55', 'name': "Côte d'Ivoire", 'totalFunding': 3818321, 'singleFunding': 3818321, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '200', 'name': 'Sierra Leone', 'totalFunding': 6614790, 'singleFunding': 6614790, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '24', 'name': 'Benin', 'totalFunding': 1606150, 'singleFunding': 1606150, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '84', 'name': 'Ghana', 'totalFunding': 952767, 'singleFunding': 952767, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    alblocation_objectsBreakdown = [{'type': 'Location', 'direction': 'destination', 'name': 'Not specified', 'totalFunding': 107894770, 'singleFunding': 107894770, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '132', 'name': 'Macedonia, The Former Yugoslav Republic of', 'totalFunding': 19506354, 'singleFunding': 19506354, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '25724802', 'name': 'Serbia and Montenegro (until 2006-2009)', 'totalFunding': 3664205, 'singleFunding': 3664205, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '3', 'name': 'Albania', 'totalFunding': 470201, 'singleFunding': 470201, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}, {'type': 'Location', 'direction': 'destination', 'id': '28', 'name': 'Bosnia and Herzegovina', 'totalFunding': 3130464, 'singleFunding': 3130464, 'overlapFunding': 0, 'sharedFunding': 0, 'onBoundaryFunding': 0}]

    afg645location_objects = [{'id': 1, 'name': 'Afghanistan', 'objectType': 'Location', 'revisedRequirements': 598923998}]

    afg544location_objects = [{'id': 25799579, 'name': 'South Eastern', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799577, 'name': 'North Eastern', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799578, 'name': 'Northern', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799581, 'name': 'Western', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799574, 'name': 'Central Highland', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 1, 'name': 'Afghanistan', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799580, 'name': 'Southern', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799576, 'name': 'Eastern', 'objectType': 'Location', 'revisedRequirements': 409413812}, {'id': 25799575, 'name': 'Capital', 'objectType': 'Location', 'revisedRequirements': 409413812}]

    cpvlocation_objects = [{'id': 24, 'name': 'Benin', 'objectType': 'Location', 'revisedRequirements': 1606150, 'origRequirements': 687585}, {'id': 36, 'name': 'Burkina Faso', 'objectType': 'Location', 'revisedRequirements': 21627280, 'origRequirements': 11094513}, {'id': 41, 'name': 'Cape Verde', 'objectType': 'Location', 'revisedRequirements': 565000, 'origRequirements': 0}, {'id': 55, 'name': "Côte d'Ivoire", 'objectType': 'Location', 'revisedRequirements': 1017000, 'origRequirements': 0}, {'id': 84, 'name': 'Ghana', 'objectType': 'Location', 'revisedRequirements': 874182, 'origRequirements': 0}, {'id': 93, 'name': 'Guinea', 'objectType': 'Location', 'revisedRequirements': 21356802, 'origRequirements': 2508846}, {'id': 94, 'name': 'Guinea-Bissau', 'objectType': 'Location', 'revisedRequirements': 9625090, 'origRequirements': 6210154}, {'id': 126, 'name': 'Liberia', 'objectType': 'Location', 'revisedRequirements': 15223613, 'origRequirements': 700000}, {'id': 137, 'name': 'Mali', 'objectType': 'Location', 'revisedRequirements': 19755994, 'origRequirements': 16906128}, {'id': 141, 'name': 'Mauritania', 'objectType': 'Location', 'revisedRequirements': 23049215, 'origRequirements': 11672826}, {'id': 162, 'name': 'Niger', 'objectType': 'Location', 'revisedRequirements': 51782808, 'origRequirements': 44497516}, {'id': 197, 'name': 'Senegal', 'objectType': 'Location', 'revisedRequirements': 13346146, 'origRequirements': 10988935}, {'id': 200, 'name': 'Sierra Leone', 'objectType': 'Location', 'revisedRequirements': 7579317, 'origRequirements': 0}, {'id': 224, 'name': 'Togo', 'objectType': 'Location', 'revisedRequirements': 3923960, 'origRequirements': 0}, {'name': 'Not specified', 'objectType': 'Location', 'revisedRequirements': 169694333, 'origRequirements': 203815172}]

    alblocation_objects = [{'name': 'Not specified', 'objectType': 'Location', 'revisedRequirements': 212686531, 'origRequirements': 236654801}]

    plan645 = {'id': 645, 'name': 'Afghanistan 2018', 'code': 'HAFG18', 'startDate': '2018-01-01T00:00:00.000Z', 'endDate': '2018-12-31T00:00:00.000Z', 'isForHPCProjects': False, 'emergencies': [], 'years': [{'id': 39, 'year': '2018'}], 'locations': [{'id': 1, 'name': 'Afghanistan', 'iso3': 'AFG', 'adminlevel': 0}], 'categories': [{'id': 4, 'name': 'Humanitarian response plan', 'group': 'planType', 'code': None}], 'revisedRequirements': 598923998, 'meta': {'language': 'en'}}

    plan544 = {'id': 544, 'name': 'Afghanistan 2017', 'code': 'HAFG17', 'startDate': '2017-01-01T00:00:00.000Z', 'endDate': '2017-12-31T00:00:00.000Z', 'isForHPCProjects': False, 'emergencies': [], 'years': [{'id': 38, 'year': '2017'}], 'locations': [{'id': 1, 'name': 'Afghanistan', 'iso3': 'AFG', 'adminlevel': 0}, {'id': 25799575, 'name': 'Capital', 'iso3': None, 'adminlevel': 1}, {'id': 25799574, 'name': 'Central Highland', 'iso3': None, 'adminlevel': 1}], 'categories': [{'id': 4, 'name': 'Humanitarian response plan', 'group': 'planType', 'code': None}], 'revisedRequirements': 409413812, 'meta': {'language': 'en'}}

    plan90 = {'id': 90, 'name': 'Southeastern Europe 2002', 'code': 'CXSEUR02', 'startDate': '2002-01-01T00:00:00.000Z', 'endDate': '2002-12-31T00:00:00.000Z', 'isForHPCProjects': False, 'emergencies': [{'id': 10, 'name': 'Southeastern Europe 2000 - 2002'}], 'years': [{'id': 23, 'year': '2002'}], 'locations': [], 'categories': [{'id': 110, 'name': 'CAP', 'group': 'planType', 'code': None}], 'origRequirements': 236654801, 'revisedRequirements': 212686531, 'meta': {'language': 'en'}}

    plan222 = {'id': 222, 'name': 'West Africa 2007', 'code': 'CXWAF07', 'startDate': '2007-01-01T00:00:00.000Z', 'endDate': '2007-12-31T00:00:00.000Z', 'isForHPCProjects': False, 'emergencies': [], 'years': [{'id': 28, 'year': '2007'}], 'locations': [{'id': 55, 'iso3': 'CIV', 'name': "Côte d'Ivoire", 'adminLevel': 0}, {'id': 126, 'iso3': 'LBR', 'name': 'Liberia', 'adminLevel': 0}, {'id': 137, 'iso3': 'MLI', 'name': 'Mali', 'adminLevel': 0}, {'id': 93, 'iso3': 'GIN', 'name': 'Guinea', 'adminLevel': 0}, {'id': 84, 'iso3': 'GHA', 'name': 'Ghana', 'adminLevel': 0}, {'id': 162, 'iso3': 'NER', 'name': 'Niger', 'adminLevel': 0}, {'id': 197, 'iso3': 'SEN', 'name': 'Senegal', 'adminLevel': 0}, {'id': 224, 'iso3': 'TGO', 'name': 'Togo', 'adminLevel': 0}, {'id': 36, 'iso3': 'BFA', 'name': 'Burkina Faso', 'adminLevel': 0}, {'id': 141, 'iso3': 'MRT', 'name': 'Mauritania', 'adminLevel': 0}, {'id': 200, 'iso3': 'SLE', 'name': 'Sierra Leone', 'adminLevel': 0}, {'id': 24, 'iso3': 'BEN', 'name': 'Benin', 'adminLevel': 0}, {'id': 41, 'iso3': 'CPV', 'name': 'Cape Verde', 'adminLevel': 0}, {'id': 94, 'iso3': 'GNB', 'name': 'Guinea-Bissau', 'adminLevel': 0}], 'categories': [{'id': 110, 'name': 'CAP', 'group': 'planType', 'code': None}], 'origRequirements': 309081675, 'revisedRequirements': 361026890, 'meta': {'language': 'en'}}

    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(hdx_read_only=True, user_agent='test',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'afg', 'title': 'Afghanistan'}, {'name': 'alb', 'title': 'Albania'}, {'name': 'cpv', 'title': 'Cape Verde'}])
        Country.countriesdata(False)

    @pytest.fixture(scope='function')
    def downloader(self):
        class Response:
            @staticmethod
            def json():
                pass

        class Download:
            @staticmethod
            def download(url):
                response = Response()
                if 'groupby' not in url and 'location' in url:
                    def fn():
                        return {'data': TestFTS.countries}
                    response.json = fn
                elif 'fts/flow?countryISO3=AFG&year=2017' in url:
                    def fn():
                        if 'nofund' in url:
                            data = {}
                        else:
                            data = TestFTS.afgflows
                        return {'data': {'flows': data}}
                    response.json = fn
                elif 'fts/flow?countryISO3=CPV&year=2018' in url:
                    def fn():
                        return {'data': {'flows': TestFTS.cpvflows}}
                    response.json = fn
                elif 'fts/flow?countryISO3=ALB&year=2018' in url:
                    def fn():
                        return {'data': {'flows': TestFTS.albflows}}
                    response.json = fn
                elif 'plan/country/AFG' in url:
                    def fn():
                        if 'noreq' in url:
                            data = []
                        else:
                            data = TestFTS.afgrequirements
                        return {'data': data}
                    response.json = fn
                elif 'plan/country/CPV' in url:
                    def fn():
                        return {'data': TestFTS.cpvrequirements}
                    response.json = fn
                elif 'plan/country/ALB' in url:
                    def fn():
                        return {'data': []}
                    response.json = fn
                elif 'fts/flow?groupby=plan&countryISO3=AFG' in url:
                    def fn():
                        if 'fundnoid' in url:
                            data = TestFTS.objectsBreakdownnoid
                        elif 'nofund' in url:
                            data = None
                        else:
                            data = TestFTS.afgobjectsBreakdown
                        return {'data': {'report3': {'fundingTotals': {'objects': [{'objectsBreakdown': data}]}}}}
                    response.json = fn
                elif 'fts/flow?groupby=plan&countryISO3=CPV' in url:
                    def fn():
                        return {'data': {'report3': {
                                'fundingTotals': {'objects': [{'objectsBreakdown': TestFTS.cpvobjectsBreakdown}]}}}}
                    response.json = fn
                elif 'fts/flow?groupby=plan&countryISO3=ALB' in url:
                    def fn():
                        return {'data': {'report3': {
                            'fundingTotals': {'objects': [{'objectsBreakdown': TestFTS.albobjectsBreakdown}]}}}}
                    response.json = fn
                elif 'fts/flow?planid=' in url:
                    def fn():
                        if 'groupby=cluster' in url:
                            fundtotaldata = {'sharedFunding': 0}
                            if 'dlerr' in url:
                                raise DownloadError()
                            if 'cpvsite' in url:
                                funddata = TestFTS.cpvcluster_objectsBreakdown
                                reqdata = TestFTS.cpvcluster_objects
                            elif 'albsite' in url:
                                funddata = TestFTS.albcluster_objectsBreakdown
                                reqdata = TestFTS.albcluster_objects
                            else:  # afgsite
                                if 'nofund' in url:
                                    funddata = []
                                else:
                                    funddata = TestFTS.afgcluster_objectsBreakdown
                                if 'noreq' in url:
                                    reqdata = {}
                                else:
                                    reqdata = TestFTS.afgcluster_objects
                        else:  # groupby=location
                            fundtotaldata = None
                            if 'cpvsite' in url:
                                funddata = TestFTS.cpvlocation_objectsBreakdown
                                reqdata = TestFTS.cpvlocation_objects
                            elif 'albsite' in url:
                                funddata = TestFTS.alblocation_objectsBreakdown
                                reqdata = TestFTS.alblocation_objects
                            else:  # afgsite
                                if 'nofund' in url:
                                    funddata = []
                                else:
                                    if '645' in url:
                                        funddata = TestFTS.afg645location_objectsBreakdown
                                    else:  # 544
                                        funddata = TestFTS.afg544location_objectsBreakdown
                                if 'noreq' in url:
                                    reqdata = {}
                                else:
                                    if '645' in url:
                                        reqdata = TestFTS.afg645location_objects
                                    else:  # 544
                                        reqdata = TestFTS.afg544location_objects

                        return {'data': {'report3': {'fundingTotals': {'objects': [{'totalBreakdown': fundtotaldata,
                                                                                    'objectsBreakdown': funddata}]}},
                                         'requirements': {'objects': reqdata}}}

                    response.json = fn
                elif 'plan/id/' in url:
                    if '645' in url:
                        plandata = TestFTS.plan645
                    elif '544' in url:
                        plandata = TestFTS.plan544
                    elif '90' in url:
                        plandata = TestFTS.plan90
                    elif '222' in url:
                        plandata = TestFTS.plan222
                    else:
                        plandata = None

                    def fn():
                        return {'data': plandata}
                    response.json = fn
                return response
        return Download()

    def test_get_countries(self, downloader):
        countries = get_countries('http://afgsite/', downloader)
        assert countries == TestFTS.countries

    def test_generate_afg_dataset_and_showcase(self, configuration, downloader):
        afgdataset = {'groups': [{'name': 'afg'}], 'name': 'fts-requirements-and-funding-data-for-afghanistan',
                      'title': 'Afghanistan - Requirements and Funding Data',
                      'tags': [{'name': 'HXL'}, {'name': 'cash assistance'},
                               {'name': 'financial tracking service - fts'}, {'name': 'funding'}],
                      'dataset_date': '06/01/2017',
                      'data_update_frequency': '1', 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                      'owner_org': 'fb7c2910-6080-4b66-8b4f-0be9b6dc4d8e', 'subnational': '0'}
        afgresources = [
            {'name': 'fts_funding_afg.csv', 'description': 'FTS Detailed Funding Data for Afghanistan for 2017',
             'format': 'csv'},
            {'name': 'fts_requirements_funding_afg.csv',
             'description': 'FTS Annual Requirements and Funding Data for Afghanistan', 'format': 'csv'},
            {'name': 'fts_requirements_funding_cluster_afg.csv',
             'description': 'FTS Annual Requirements and Funding Data by Cluster for Afghanistan', 'format': 'csv'}]
        afgshowcase = {
            'image_url': 'https://fts.unocha.org/sites/default/files/styles/fts_feature_image/public/navigation_101.jpg',
            'name': 'fts-requirements-and-funding-data-for-afghanistan-showcase',
            'notes': 'Click the image on the right to go to the FTS funding summary page for Afghanistan',
            'url': 'https://fts.unocha.org/countries/1/flows/2017', 'title': 'FTS Afghanistan Summary Page',
            'tags': [{'name': 'HXL'}, {'name': 'cash assistance'}, {'name': 'financial tracking service - fts'},
                     {'name': 'funding'}]}

        def compare_afg(dataset, showcase, hxl_resource, expected_resources=afgresources, expected_hxl_resource='fts_requirements_funding_cluster_afg.csv', prefix=''):
            assert dataset == afgdataset
            resources = dataset.get_resources()
            assert resources == expected_resources
            if prefix:
                prefix = '%s_' % prefix
            for resource in resources:
                expected_file = join('tests', 'fixtures', '%s%s' % (prefix, resource['name']))
                actual_file = join(folder, resource['name'])
                assert_files_same(expected_file, actual_file)
            assert showcase == afgshowcase
            assert hxl_resource == expected_hxl_resource

        with temp_dir('fts') as folder:
            today = datetime.strptime('01062017', '%d%m%Y').date()
            test = 'nofundnoreq'
            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://%s/' % test, downloader, folder, 'AFG', 'Afghanistan', 1, today)
            assert dataset is None
            assert showcase is None
            assert hxl_resource is None
            test = 'nofund'
            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://%s/' % test, downloader, folder, 'AFG', 'Afghanistan', 1, today)
            compare_afg(dataset, showcase, hxl_resource, expected_resources=afgresources[1:], expected_hxl_resource=None, prefix=test)
            test = 'noreq'
            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://%s/' % test, downloader, folder, 'AFG', 'Afghanistan', 1, today)
            compare_afg(dataset, showcase, hxl_resource, expected_hxl_resource=None, prefix=test)

            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://afgsite/', downloader, folder, 'AFG', 'Afghanistan', 1, today)
            compare_afg(dataset, showcase, hxl_resource)

    def test_generate_cpv_dataset_and_showcase(self, configuration, downloader):
        with temp_dir('fts') as folder:
            today = datetime.strptime('01062018', '%d%m%Y').date()
            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://cpvsite/', downloader, folder, 'CPV', 'Cape Verde', 1, today)
            assert dataset == {'groups': [{'name': 'cpv'}], 'name': 'fts-requirements-and-funding-data-for-cape-verde',
                               'title': 'Cape Verde - Requirements and Funding Data',
                               'tags': [{'name': 'HXL'}, {'name': 'cash assistance'}, {'name': 'financial tracking service - fts'}, {'name': 'funding'}], 'dataset_date': '06/01/2018',
                               'data_update_frequency': '1', 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                               'owner_org': 'fb7c2910-6080-4b66-8b4f-0be9b6dc4d8e', 'subnational': '0'}

            resources = dataset.get_resources()
            assert resources == [{'name': 'fts_funding_cpv.csv', 'description': 'FTS Detailed Funding Data for Cape Verde for 2018', 'format': 'csv'},
                                 {'name': 'fts_requirements_funding_cpv.csv', 'description': 'FTS Annual Requirements and Funding Data for Cape Verde', 'format': 'csv'}]
            for resource in resources:
                resource_name = resource['name']
                expected_file = join('tests', 'fixtures', resource_name)
                actual_file = join(folder, resource_name)
                assert_files_same(expected_file, actual_file)

            assert showcase == {'image_url': 'https://fts.unocha.org/sites/default/files/styles/fts_feature_image/public/navigation_101.jpg',
                                'name': 'fts-requirements-and-funding-data-for-cape-verde-showcase',
                                'notes': 'Click the image on the right to go to the FTS funding summary page for Cape Verde',
                                'url': 'https://fts.unocha.org/countries/1/flows/2018', 'title': 'FTS Cape Verde Summary Page',
                                'tags': [{'name': 'HXL'}, {'name': 'cash assistance'}, {'name': 'financial tracking service - fts'}, {'name': 'funding'}]}
            assert hxl_resource is None

    def test_generate_alb_dataset_and_showcase(self, configuration, downloader):
        with temp_dir('fts') as folder:
            today = datetime.strptime('01062018', '%d%m%Y').date()
            dataset, showcase, hxl_resource = generate_dataset_and_showcase('http://albsite/', downloader, folder, 'ALB', 'Albania', 1, today)
            assert dataset == {'groups': [{'name': 'alb'}], 'name': 'fts-requirements-and-funding-data-for-albania',
                               'title': 'Albania - Requirements and Funding Data',
                               'tags': [{'name': 'HXL'}, {'name': 'cash assistance'}, {'name': 'financial tracking service - fts'}, {'name': 'funding'}], 'dataset_date': '06/01/2018',
                               'data_update_frequency': '1', 'maintainer': '196196be-6037-4488-8b71-d786adf4c081',
                               'owner_org': 'fb7c2910-6080-4b66-8b4f-0be9b6dc4d8e', 'subnational': '0'}

            resources = dataset.get_resources()
            assert resources == [{'name': 'fts_funding_alb.csv', 'description': 'FTS Detailed Funding Data for Albania for 2018', 'format': 'csv'},
                                 {'name': 'fts_requirements_funding_alb.csv', 'description': 'FTS Annual Requirements and Funding Data for Albania', 'format': 'csv'}]
            for resource in resources:
                resource_name = resource['name']
                expected_file = join('tests', 'fixtures', resource_name)
                actual_file = join(folder, resource_name)
                assert_files_same(expected_file, actual_file)

            assert showcase == {'image_url': 'https://fts.unocha.org/sites/default/files/styles/fts_feature_image/public/navigation_101.jpg',
                                'name': 'fts-requirements-and-funding-data-for-albania-showcase',
                                'notes': 'Click the image on the right to go to the FTS funding summary page for Albania',
                                'url': 'https://fts.unocha.org/countries/1/flows/2018', 'title': 'FTS Albania Summary Page',
                                'tags': [{'name': 'HXL'}, {'name': 'cash assistance'}, {'name': 'financial tracking service - fts'}, {'name': 'funding'}]}
            assert hxl_resource is None
