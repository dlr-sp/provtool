import json
import logging
import os
import sys

from typing import Dict, List

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


class Validator:

    def __init__(self, filelocation: str = ''):
        self.logger = logging.getLogger('Validator')
        fh = logging.FileHandler('Validator.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.WARNING)

        self._filelocation = filelocation

    def read_provanddata(self, pcid):
        discovered_plugins = entry_points(group='provtoolutils.reader')
        for dp in discovered_plugins:
            if dp.name == 'file':
                if not os.path.exists(self._filelocation):
                    self.logger.warning('Found reader for file type but to filelocation given')
                    continue
                try:
                    pr, dr, err = dp.load().read_provanddata({'directory': self._filelocation}, pcid)
                    return pr, dr, err
                # Catch any exception. These may come from arbitrary plugins and may be unpredictable. On
                # the other hand the integrity of a container (data and provenance) can always be checked.
                # Therefore, if any of the readers return without an error, it is sufficient.
                except Exception as e:
                    print(e)

        return None, None, True

    def check(self, pcid) -> List[Dict]:
        """
            Result is returned in json-compatible schema. See: constants.py: report_schema
        """
        known_ids = {}

        def _check(pcid: str, ancestors: List[str], report_entries: List[str], used_by=None):
            if pcid in known_ids:
                if used_by is not None:
                    known_ids[pcid]['used_by'].append(used_by)
                return known_ids[pcid]['valid']

            entity_name = 'UNKNOWN'
            entity_datahash = 'UNKNOWN'
            act_name = 'UNKNOWN'
            start_time = None
            end_time = None
            used = []
            entry = {'entity': pcid, 'data': entity_datahash, 'name': entity_name, 'valid': False,
                     'used_by': [used_by], 'activity': act_name,
                     'start_time': start_time, 'end_time': end_time, 'used': used}
            known_ids[pcid] = entry

            try:
                pr, dr, err = self.read_provanddata(pcid)
                if err:
                    raise ValueError(f'Error reading the provenance file {pcid}')
                provenance = json.loads(pr)
                entity = next(iter(provenance['entity'].values()))
                entry['entity_name'] = entity['prov:label']
                entry['entity_datahash'] = entity['provtool:datahash']

                ancestors.append(pcid)
                entry['act_name'] = next(iter(provenance['activity'].values()))['prov:label']
                entry['start_time'] = next(iter(provenance['activity'].values()))['prov:startTime']
                entry['end_time'] = next(iter(provenance['activity'].values()))['prov:endTime']
                if 'used' in provenance:
                    entry['used'] = [u['prov:entity'] for u in provenance['used'].values()]
                    for u in provenance['used'].values():
                        # Check, if used entities are valid
                        result_of_used = _check(u['prov:entity'], ancestors, report_entries, pcid)
                        if not result_of_used:
                            self.logger.warning(f"Used resource not valid: Expecting {u['prov:entity']} for {pcid}")
                            report_entries.append(entry)
                            return False

                entry['valid'] = True
                report_entries.append(entry)
                return True
            except ValueError as e:
                self.logger.warning('Problems with processing {}'.format(pcid))
                self.logger.warning(e)
                report_entries.append(entry)
                return False

        report_entries = []
        _check(pcid, [], report_entries)

        # Dedup and merge used_by
        deduped = {}
        for re in report_entries:
            key = str(re['entity']) + str(re['name']) + str(re['valid'])
            if key in deduped:
                deduped[key]['used_by'] = deduped[key]['used_by'] + re['used_by']
            else:
                deduped[key] = re

        for v in deduped.values():
            v['used_by'] = [u for u in v['used_by'] if u is not None]

        return report_entries
