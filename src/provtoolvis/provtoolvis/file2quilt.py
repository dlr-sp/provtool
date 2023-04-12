import argparse
import json
import jsonschema
import logging
import os
import sys
import traceback

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from provtoolvis import create_image

from typing import Dict, List, Set, Tuple

from provtoolutils.constants import prov_schema
from provtoolutils.quilt import Matrix
from provtoolutils.utilities import convert_rawprov2containerprov


def read_provanddata(options, cid):
    discovered_plugins = entry_points(group='provtoolutils.reader')
    for dp in discovered_plugins:
        try:
            pr, dr, err = getattr(dp.load(), 'read_provanddata')(options, cid)
            if pr is None:
                continue
            return pr, dr, err
        # Catch any exception. These may come from arbitrary plugins and may be unpredictable. On
        # the other hand the integrity of a container (data and provenance) can always be checked.
        # Therefore, if any of the readers return without an error, it is sufficient.
        except Exception as e:
            print(e)

    print(f'Not found: {cid}')
    return None, None, True


def _setup_logging():
    # Create a custom logger
    logger = logging.getLogger('visualisation')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('visualisation.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


def find_prov_ids_recursive(options: dict, cid: str) -> List[str]:
    """
    Searches recursively through a provenance graph and reports the container ids found.
    :param options: A dictionary containing an id and all the parameters to resolve the provenace
    graph.
    :return: The ids of the provenance containers.
    """
    prov_ids = []
    to_scan = [cid]
    used = set()
    while len(to_scan) > 0:
        cid = to_scan.pop()
        used.add(cid)
        prov_ids.append(cid)
        pr, _, err = read_provanddata(options, cid)

        j = json.loads(convert_rawprov2containerprov(pr))
        if 'used' in j:
            for u in j['used'].values():
                to_scan.append(u['prov:entity'])

    return prov_ids


def search_prov_files_for_relations(options, prov_ids: List[str]) -> Tuple[Set[str], Dict[str, str],
                                                                           Dict[str, str], Dict[str, str],
                                                                           Dict[str, str]]:
    logger = _setup_logging()
    activities = set()
    activities.add('UNKNOWN_ACTIVITY')
    agents = set()
    agents.add('UNKNOWN_AGENT')
    generations = {}
    used = {}
    act2ag = {'UNKNOWN_ACTIVITY': 'UNKNOWN_AGENT'}
    act2ag_trans = {}
    id2label = {'UNKNOWN_ACTIVITY': 'Unknown activity', 'UNKNOWN_AGENT': 'Unknown agent'}
    for pf in prov_ids:
        pr, _, err = read_provanddata(options, pf)
        if err:
            logger.warn(f'Problems while reading {pf}')
        j = json.loads(convert_rawprov2containerprov(pr))
        try:
            jsonschema.validate(j, prov_schema)
        except jsonschema.ValidationError:
            logger.warning('Invalid schema for {}'.format(pf))
            traceback.print_exc()
            continue
        act = next(iter(j['activity'].values()))
        act['id'] = next(iter(j['activity'].keys()))
        activities.add(act['id'])
        id2label[act['id']] = act['prov:label']
        entity = next(iter(j['entity'].values()))
        entity['id'] = os.path.basename(pf).replace('.prov', '')
        id2label[entity['id']] = entity['prov:label']

        for k, v in j['agent'].items():
            agents.add(k)
            id2label[k] = v['prov:label']

        # Not exact. There could be more than 1 person as agent, for example in a actedOnBehalfOf-relation.
        act2ag[act['id']] = [ag for ag, props in j['agent'].items() if props['prov:type'] == 'prov:Person'][0]

        generations[entity['id']] = act['id']
        if 'used' in j:
            for u in j['used'].values():
                li = used.get(u['prov:activity'], set())
                li.add(u['prov:entity'])
                used[u['prov:activity']] = li

                if not u['prov:entity'] in id2label:
                    id2label[u['prov:entity']] = u['prov:entity']
                if not u['prov:entity'] in generations:
                    generations[u['prov:entity']] = 'UNKNOWN_ACTIVITY'

    for k, v in act2ag.items():
        act2ag_trans[id2label[k]] = id2label[v]

    return set(agents), activities, used, generations, act2ag, act2ag_trans, id2label


def find_relevant_ids(specified_entity, used, generations, act2ag, logger: logging.Logger = None):
    used_for_specified_entity = [specified_entity]
    ents = [specified_entity]
    while len(ents) > 0:
        acts = []
        try:
            for e in ents:
                if e in generations:
                    a = generations[e]
                else:
                    a = 'UNKNOWN_ACTIVITY'
                acts.append(a)
                used_for_specified_entity.append(act2ag[a])
            used_for_specified_entity.extend(acts)
        except KeyError as ke:
            if logger:
                logger.error(f'Could not find {e} in generations list. Most probably, the file {e} ' +
                             'is missing in the directories searched or the provenance information ' +
                             'in the file is incorrect')
            raise ke

        ents = []
        for a in acts:
            # Only take into account activities which use something.
            if a in used:
                ents.extend(used[a])
        used_for_specified_entity.extend(ents)

    return used_for_specified_entity


def find_relevant_usage_and_generation(relevant_ids, used, generations):
    rgen = {}
    ru = {}
    for k, v in generations.items():
        if k in relevant_ids and v in relevant_ids:
            rgen[k] = v

    for k, v in used.items():
        if k in relevant_ids:
            ru[k] = [_v for _v in v if _v in relevant_ids]

    return ru, rgen


def create_matrices(activities, relevant_used, relevant_generations, used_for_specified_entity, id2label):
    available = []
    start_activities = [a for a in activities if a not in relevant_used and a in used_for_specified_entity]
    cur_act = [a for a in start_activities]
    matrices = []
    before = []
    while len(cur_act) > 0:
        ml = {}
        mr = {}
        cur_gen_ent = [k for k, v in relevant_generations.items() if v in cur_act]

        for k, v in relevant_generations.items():
            if v in cur_act:
                ml[cur_gen_ent.index(k), cur_act.index(v)] = id2label[k]
        for k, f in relevant_used.items():
            off = len(before)
            for e in f:
                if k in cur_act:
                    if e in before:
                        mr[before.index(e), cur_act.index(k)] = id2label[e]
                    else:
                        mr[off, cur_act.index(k)] = id2label[e]
                        off = off + 1

        matrices.append(Matrix(left_header=[id2label[c] for c in cur_gen_ent],
                               right_header=[id2label[c] for c in before], left=ml, right=mr,
                               elements=[id2label[c] for c in cur_act]))
        available.extend(cur_gen_ent)
        before = cur_gen_ent
        cur_act = sorted([k for k, v in relevant_used.items()
                          if len(set(cur_gen_ent) - set(v)) < len(set(cur_gen_ent)) and
                          len(set(v) - set(available)) == 0])

    matrices.reverse()

    return matrices


def main(target_id, image_file, args):
    prov_ids = find_prov_ids_recursive(args, target_id)
    agents, activities, used, generations, act2ag, act2ag_trans, id2label = \
        search_prov_files_for_relations(args, prov_ids)

    used_for_specified_entity = find_relevant_ids(target_id, used, generations, act2ag)
    relevant_used, relevant_generations = find_relevant_usage_and_generation(used_for_specified_entity,
                                                                             used, generations)

    matrices = create_matrices(activities, relevant_used, relevant_generations, used_for_specified_entity, id2label)
    create_image.create_image(matrices, [id2label[a] for a in agents if a in used_for_specified_entity],
                              act2ag_trans, image_file)


class ReaderAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        ex = getattr(namespace, self.dest)
        if ex is None:
            ex = {}
        sp = values.split('=')
        if len(sp) == 2:
            ex[sp[0]] = sp[1]
        setattr(namespace, self.dest, ex)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target_id')
    parser.add_argument('image_file')
    parser.add_argument('--reader', nargs='+', action=ReaderAction)

    args = parser.parse_args()

    logger = _setup_logging()

    main(args.target_id, args.image_file, args.reader)
