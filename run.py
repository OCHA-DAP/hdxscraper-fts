#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
REGISTER:
---------

Caller script. Designed to call all other functions
that register datasets in HDX.

'''
import logging
from datetime import datetime
from os.path import join, expanduser

from hdx.hdx_configuration import Configuration
from hdx.utilities.downloader import Download
from hdx.utilities.path import progress_storing_tempdir

from fts.download import FTSDownload
from fts.locations import Locations
from fts.main import FTS

from hdx.facades.simple import facade

logger = logging.getLogger(__name__)

lookup = 'hdx-scraper-fts'


def main():
    '''Generate dataset and create it in HDX'''

    with Download(extra_params_yaml=join(expanduser('~'), '.extraparams.yml'), extra_params_lookup=lookup, rate_limit={'calls': 1, 'period': 1}) as downloader:
        configuration = Configuration.read()
        ftsdownloader = FTSDownload(configuration, downloader)
        notes = configuration['notes']
        today = datetime.now()

        locations = Locations(ftsdownloader)
        logger.info('Number of country datasets to upload: %d' % len(locations.countries))

        fts = FTS(ftsdownloader, locations, today, notes)
        for info, country in progress_storing_tempdir('FTS', locations.countries, 'iso3'):
            folder = info['folder']
# for testing specific countries only
#             if nextdict['iso3'] not in ['AFG', 'JOR', 'TUR', 'PHL', 'SDN', 'PSE']:
#                 continue
            dataset, showcase, hxl_resource = fts.generate_dataset_and_showcase(folder, country)
            if dataset is not None:
                dataset.update_from_yaml()
                if hxl_resource is None:
                    dataset.preview_off()
                else:
                    dataset.set_quickchart_resource(hxl_resource)
                dataset.create_in_hdx(remove_additional_resources=True, hxl_update=False,
                                      updated_by_script='HDX Scraper: FTS', batch=info['batch'])
                resources = sorted(dataset.get_resources(), key=lambda x: len(x['name']), reverse=True)
                if hxl_resource and 'cluster' not in hxl_resource['name']:
                    hxl_update = True
                else:
                    hxl_update = False
                resource_ids = [x['id'] for x in resources]
                dataset.reorder_resources(resource_ids, hxl_update=hxl_update)
                if hxl_resource and not hxl_update:
                    dataset.generate_resource_view()
                showcase.create_in_hdx()
                showcase.add_dataset(dataset)


if __name__ == '__main__':
    facade(main, user_agent_config_yaml=join(expanduser('~'), '.useragents.yml'), user_agent_lookup=lookup, project_config_yaml=join('config', 'project_configuration.yml'))

