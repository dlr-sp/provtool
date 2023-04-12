import datetime
import json
import jsonschema
import os
import pandas
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from typing import List

from provtoolutils.constants import model_encoding, prov_schema
from provtoolutils.utilities import calculate_data_hash, convert_rawprov2containerprov


def read_provanddata():
    discovered_plugins = entry_points(group='provtoolutils.reader')
    f = getattr(discovered_plugins['file'].load(), 'read_provanddata')

    return f


def _gather(prov_filepaths, default_time, callback):
    dircontainers = []

    for prov_filepath in prov_filepaths:
        with open(prov_filepath, 'rb') as provfile:
            jsonschema.validate(json.loads(provfile.read().decode(model_encoding)), prov_schema)

    for prov_filepath in prov_filepaths:
        validcontainer = True

        pr, dr, err = read_provanddata()({'directory': os.path.dirname(prov_filepath)},
                                         os.path.basename(prov_filepath).replace('.prov', ''))
        if err:
            raise ValueError(f'Could not read provenance container {prov_filepath}')
        prov = json.loads(convert_rawprov2containerprov(pr))

        exp_filename = os.path.basename(prov_filepath,).replace('.prov', '')
        if not exp_filename == next(iter(prov['entity'].keys())):
            validcontainer = False

        activities = [e for e in prov['activity'].values()]
        # Replace values, which should not be taken into account when comparing the provenance
        # with default values.
        activities[0]['prov:startTime'] = datetime.datetime.strftime(default_time, '%Y-%m-%dT%H:%M:%S%z')
        activities[0]['prov:endTime'] = datetime.datetime.strftime(default_time, '%Y-%m-%dT%H:%M:%S%z')
        prov['activity'] = {'act_placeholder': activities[0]}

        entities = [e for e in prov['entity'].values()]
        prov['entity'] = {'ent_placeholder': entities[0]}

        wasGeneratedBy = [e for e in prov['wasGeneratedBy'].values()]
        wasGeneratedBy[0]['prov:activity'] = 'act_placeholder'
        wasGeneratedBy[0]['prov:entity'] = 'ent_placeholder'
        prov['wasGeneratedBy'] = {'wGB_placeholder': wasGeneratedBy[0]}

        if 'used' in prov:
            new_used_flattened = []
            for us in [u for u in prov['used'].values()]:
                us['prov:activity'] = 'act_placeholder'
                new_used_flattened.append(us['prov:entity'])

            new_used_flattened.sort()
            prov['used'] = ''.join(new_used_flattened)

        for waw in [w for w in prov['wasAssociatedWith'].values()]:
            if 'prov:activity' in waw:
                waw['prov:activity'] = 'act_placeholder'

        if 'wasStartedBy' in prov:
            wasStartedBy = [e for e in prov['wasStartedBy'].values()]
            wasStartedBy[0]['prov:activity'] = 'act_placeholder'
            wasStartedBy[0]['prov:starter'] = 'starter_placeholder'

        if callback is not None:
            entities[0]['provtool:datahash'] = calculate_data_hash(callback(entities[0]['prov:label'], dr))
        else:
            entities[0]['provtool:datahash'] = calculate_data_hash(dr)

        provenancehash = calculate_data_hash(json.dumps(prov, ensure_ascii=False, sort_keys=True).encode('utf-8'))
        datahash = entities[0]['provtool:datahash']
        dircontainers.append({'provenancehash': provenancehash, 'datahash': datahash,
                              'filename': os.path.basename(prov_filepath),
                              'label': entities[0]['prov:label'], 'validcontainer': validcontainer})

    return dircontainers


def dircompare(dir_left: str, dir_right: str, callback=None) -> pandas.DataFrame:
    """
    Compare two folders with provenance containers recursively. First:  Unpack each container,
    apply the given callback to normalise data and do some provenance normalisation
    (timestamps, ...). Second: Calculate hash over provenance and data separately. Third: Merge
    the result with respect to data and provenance hash and assign matching attribute.

    Return a pandas data frame.

    Keyword arguments:
        dir_left -- the first directory
        dir_right -- the second directory
    """
    if not os.path.exists(dir_left):
        raise FileNotFoundError(f'Invalid argument: The directory {dir_left} does not exists')
    if not os.path.exists(dir_right):
        raise FileNotFoundError(f'Invalid argument: The directory {dir_right} does not exists')

    default_time = datetime.datetime.now(datetime.timezone.utc)

    prov_filepaths_left = []
    for dirpath, dirnames, filenames in os.walk(dir_left):
        for filename in [fn for fn in filenames if fn.endswith('.prov')]:
            prov_filepaths_left.append(os.path.join(dirpath, filename))
    prov_filepaths_right = []
    for dirpath, dirnames, filenames in os.walk(dir_right):
        for filename in [fn for fn in filenames if fn.endswith('.prov')]:
            prov_filepaths_right.append(os.path.join(dirpath, filename))

    dir_left_container = pandas.DataFrame(_gather(prov_filepaths_left, default_time, callback),
                                          columns=['provenancehash', 'datahash', 'filename',
                                                   'label', 'validcontainer'])
    dir_right_container = pandas.DataFrame(_gather(prov_filepaths_right, default_time, callback),
                                           columns=['provenancehash', 'datahash', 'filename',
                                                    'label', 'validcontainer'])

    valid_dir_left_container = dir_left_container[dir_left_container['validcontainer']]
    valid_dir_right_container = dir_right_container[dir_right_container['validcontainer']]
    merged = pandas.merge(
            valid_dir_left_container,
            valid_dir_right_container,
            how='outer',
            suffixes=['_left', '_right'],
            left_on=['provenancehash', 'datahash'],
            right_on=['provenancehash', 'datahash']
    )
    merged.append(dir_left_container[~dir_left_container['validcontainer']].
                  rename(columns={'filename': 'filename_left'}))
    merged.append(dir_right_container[~dir_right_container['validcontainer']].
                  rename(columns={'filename': 'filename_right'}))

    merged['matching'] = ~(merged['filename_left'].isnull() | merged['filename_right'].isnull())

    return merged


def filescompare(prov_filepaths_left: List[str], prov_filepaths_right: List[str], callback=None) -> pandas.DataFrame:
    """
    Compare two lists of provenance containers. First:  Unpack each container,
    apply the given callback to normalise data and do some provenance normalisation
    (timestamps, ...). Second: Calculate hash over provenance and data separately. Third: Merge
    the result with respect to data and provenance hash and assign matching attribute.

    Return a pandas data frame.

    Keyword arguments:
        prov_filepaths_left -- the first set
        prov_filepaths_right, -- the second set
    """
    default_time = datetime.datetime.now(datetime.timezone.utc)

    dir_left_container = pandas.DataFrame(_gather(prov_filepaths_left, default_time, callback),
                                          columns=['provenancehash', 'datahash', 'filename',
                                                   'label', 'validcontainer'])
    dir_right_container = pandas.DataFrame(_gather(prov_filepaths_right, default_time, callback),
                                           columns=['provenancehash', 'datahash', 'filename',
                                                    'label', 'validcontainer'])

    merged = pandas.merge(
            dir_left_container[dir_left_container['validcontainer']],
            dir_right_container[dir_right_container['validcontainer']],
            how='outer',
            suffixes=['_left', '_right'],
            left_on=['provenancehash', 'datahash'],
            right_on=['provenancehash', 'datahash']
    )

    merged.append(dir_left_container[~dir_left_container['validcontainer']].
                  rename(columns={'filename': 'filename_left'}))
    merged.append(dir_right_container[~dir_right_container['validcontainer']].
                  rename(columns={'filename': 'filename_right'}))

    merged['matching'] = ~(merged['filename_left'].isnull() | merged['filename_right'].isnull())

    return merged
