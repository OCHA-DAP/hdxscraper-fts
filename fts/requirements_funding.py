import logging

from fts.helpers import hxl_names

logger = logging.getLogger(__name__)


class RequirementsFunding:
    def __init__(self, downloader, locations, today):
        self.downloader = downloader
        self.locations = locations
        self.today = today

    def add_country_requirements_funding(self, planid, plan, countries):
        if len(countries) == 1:
            requirements = plan.get('requirements')
            if requirements is not None:
                requirements = requirements.get('revisedRequirements')
            funding = plan.get('funding')
            if funding is None:
                progress = None
            else:
                progress = funding.get('progress')
                funding = funding.get('totalFunding')
            countries[0]['requirements'] = requirements
            countries[0]['funding'] = funding
            countries[0]['percentFunded'] = progress
        else:
            if plan.get('customLocationCode') in ['GLBL', 'COVD']:
                return
            funding_url = f'fts/flow?planid={planid}&groupby=location'
            data = self.downloader.download_data(funding_url)
            requirements = data.get('requirements')
            country_requirements = dict()
            if requirements is not None:
                for req_object in requirements.get('objects', list()):
                    country_id = self.locations.get_countryid_from_object(req_object)
                    country_req = req_object.get('revisedRequirements')
                    if country_id is not None and country_req is not None:
                        country_requirements[country_id] = country_req
            fund_objects = data['report3']['fundingTotals']['objects']
            country_funding = dict()
            if len(fund_objects) == 1:
                for fund_object in fund_objects[0].get('objectsBreakdown', list()):
                    country_id = self.locations.get_countryid_from_object(fund_object)
                    country_fund = fund_object.get('totalFunding')
                    if country_id is not None and country_fund is not None:
                        country_funding[int(country_id)] = country_fund
            for country in countries:
                countryid = country['id']
                requirements = country_requirements.get(countryid)
                country['requirements'] = requirements
                funding = country_funding.get(countryid)
                country['funding'] = funding
                if requirements is not None and funding is not None:
                    country['percentFunded'] = funding / requirements * 100

    def get_country_funding(self, countryid, plans_by_year, start_year=2010):
        funding_by_year = dict()
        if plans_by_year is not None:
            start_year = sorted(plans_by_year.keys())[0]
        for year in range(self.today.year, start_year, -11):
            data = self.downloader.download_data(f'country/{countryid}/summary/trends/{year}', use_v2=True)
            for object in data:
                year = object['year']
                if year < start_year:
                    continue
                funding_by_year[object['year']] = object['totalFunding']
        return funding_by_year

    def generate_requirements_funding_resource(self, folder, dataset, plans_by_year, country):
        countryiso = country['iso3']
        funding_by_year = self.get_country_funding(country['id'], plans_by_year)
        rows = list()
        for year, plans in plans_by_year.items():
            not_specified_funding = funding_by_year[year]
            for plan in plans:
                planid = plan['id']
                for country in plan['countries']:
                    if country['iso3'] != countryiso:
                        continue
                    requirements = country.get('requirements', '')
                    funding = country.get('funding', '')
                    percentFunded = country.get('percentFunded', '')
                    if funding != '' and not_specified_funding is not None:
                        not_specified_funding -= funding
                    row = {'countryCode': countryiso, 'id': planid, 'name': plan['name'], 'code': plan['code'],
                           'startDate': plan['startDate'], 'endDate': plan['endDate'], 'year': year,
                           'requirements': requirements, 'funding': funding, 'percentFunded': percentFunded}
                    rows.append(row)
                    break
            if not_specified_funding is None:
                not_specified_funding = ''
            row = {'countryCode': countryiso, 'id': '', 'name': '', 'code': '',
                   'startDate': '', 'endDate': '', 'year': year,
                   'requirements': '', 'funding': not_specified_funding, 'percentFunded': ''}
            rows.append(row)
        if rows:
            headers = rows[0].keys()
            filename = 'fts_requirements_funding_%s.csv' % countryiso.lower()
            resourcedata = {
                'name': filename.lower(),
                'description': 'FTS Annual Requirements and Funding Data for %s' % country['name'],
                'format': 'csv'
            }
            success, results = dataset.generate_resource_from_iterator(headers, rows, hxl_names, folder, filename, resourcedata)
            return results['resource']
        return None
