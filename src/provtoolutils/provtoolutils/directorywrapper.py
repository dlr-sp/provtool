import argparse
import datetime
import dateutil.parser
import json
import jsonschema
import logging
import os
import textwrap
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from typing import List, Set

from collections import namedtuple

from provtoolutils.constants import agent_schema, config_schema, model_encoding
from provtoolutils.model import make_provstring, ActingSoftware, Activity, Entity,\
                                Organization, Person, ProvIdentifiableObject
from provtoolutils.utilities import calculate_data_hash


def read_provanddata(options, cid):
    discovered_plugins = entry_points(group='provtoolutils.reader')
    for dp in discovered_plugins:
        try:
            pr, dr, err = getattr(dp.load(), 'read_provanddata')(options, cid)
            return pr, dr, err
        # Catch any exception. These may come from arbitrary plugins and may be unpredictable. On
        # the other hand the integrity of a container (data and provenance) can always be checked.
        # Therefore, if any of the readers return without an error, it is sufficient.
        except Exception as e:
            print(e)

    return None, None, True


class DirectoryWrapper:
    """
    Can wrap around a non provenance aware program to generate the provenance information for the output files.

    The following assumptions are made:
        - A defined process produced output data (files) based on input data (files). The input files and the output
          files are in a separate directory each.
        - Each input file is available in the prov-container format. Only the data in the prov-container format is
          treated as input data.
        - An optional config file provides the static provenance information about the agent and the activity.
    """

    def _init_logger():
        logger = logging.getLogger('DirectoryWrapper')
        fh = logging.FileHandler('DirectoryWrapper.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)
        logger.setLevel(logging.DEBUG)

        return logger

    _logger = _init_logger()

    def __init__(self, agentinfo_filepath=None, config_filepath=None):
        self.agentinfo_filepath = agentinfo_filepath

        if agentinfo_filepath is not None:
            with open(agentinfo_filepath, 'r', encoding='utf-8') as f:
                self.agentinfo_content = f.read()

        if config_filepath is not None:
            with open(config_filepath, 'r', encoding='utf-8') as f:
                self.config_content = f.read()
            try:
                prov = json.loads(self.config_content)
                jsonschema.validate(prov, config_schema)
                self.activity = prov['activity']
            except jsonschema.exceptions.ValidationError as e:
                error = RuntimeError(f'Failed to validate configuration file {config_filepath}')
                DirectoryWrapper._logger.error(error)
                DirectoryWrapper._logger.error(e)
                raise error

            config_agent = DirectoryWrapper._parse_agentinfo(self.config_content)
            self.__provagent = config_agent

            if agentinfo_filepath is not None:
                prov = json.loads(self.agentinfo_content)
                try:
                    jsonschema.validate(prov, agent_schema)
                except jsonschema.exceptions.ValidationError as e:
                    error = RuntimeError(f'Failed to validate configuration file {agentinfo_filepath}')
                    DirectoryWrapper._logger.error(error)
                    DirectoryWrapper._logger.error(e)
                    raise error
            if agentinfo_filepath is not None:
                agent = DirectoryWrapper._parse_agentinfo(self.agentinfo_content)
            else:
                agent = None
            if agent is not None:
                if self.__provagent is not None:
                    ag = self.__provagent
                    while ag.acted_on_behalf_of is not None:
                        ag = ag.acted_on_behalf_of
                    ag.acted_on_behalf_of = agent
                else:
                    self.__provagent = agent

            if self.__provagent is None:
                error = RuntimeError(f'No agent defined in either {agentinfo_filepath} or {config_filepath}')
                DirectoryWrapper._logger.error(error)
                raise error

    @staticmethod
    def _parse_agentinfo(agentinfo_content):
        def single_agent(ag):
            if ag['type'] == 'person':
                if 'acted_on_behalf_of' in ag:
                    return Person(given_name=ag['given_name'], family_name=ag['family_name'],
                                  acted_on_behalf_of=single_agent(ag['acted_on_behalf_of'])
                                  )
                else:
                    return Person(given_name=ag['given_name'], family_name=ag['family_name'], acted_on_behalf_of=None)
            if ag['type'] == 'software':
                if 'acted_on_behalf_of' in ag:
                    return ActingSoftware(acted_on_behalf_of=single_agent(ag['acted_on_behalf_of']),
                                          creator=ag['creator'], version=ag['version'],
                                          label=ag['label'], location=ag['location']
                                          )
                else:
                    return ActingSoftware(acted_on_behalf_of=None, creator=ag['creator'],
                                          version=ag['version'], label=ag['label'], location=ag['location']
                                          )
            if ag['type'] == 'organization':
                return Organization(name=ag['label'])
            return None

        config = json.loads(agentinfo_content)
        if 'agent' not in config:
            DirectoryWrapper._logger.warn(f'Config file {agentinfo_content} contains no agent section')
            return None

        sa = single_agent(config['agent'])
        return sa

    def prov2plain(self, input_dirpath, extract=True) -> Set:
        """
        """
        result_used = set()

        for dirname, dirnames, filenames in os.walk(input_dirpath):
            prov_files = [os.path.join(dirname, f) for f in filenames]
            for pf in prov_files:
                if pf.endswith('.prov'):
                    DirectoryWrapper._logger.info('Reading provenance file: {}'.format(pf))
                    pr, dr, err = read_provanddata({'directory': os.path.dirname(pf)},
                                                   os.path.basename(pf).replace('.prov', ''))
                    if err:
                        raise ValueError('Error reading prov file')
                    target_filename = json.loads(pr.decode(model_encoding))['entity']['self']['prov:label']
                    _stf = [x for x in target_filename if x.isalnum() or x in ['.', ' ', '_', '-']]
                    sanitized_target_filename = ''.join(_stf)
                    if target_filename != sanitized_target_filename:
                        raise ValueError(f'Error. Label of entity is not sane. Got {target_filename}, ' +
                                         f'but something like {sanitized_target_filename} is needed')
                    target_filepath = os.path.join(os.path.dirname(pf), target_filename)

                    result_used.add(calculate_data_hash(pr))

                    if extract:
                        if os.path.exists(target_filepath):
                            raise FileExistsError(f'Unpacking of {pf} would lead to overwritten ' +
                                                  f'existing file {target_filepath}')
                        with open(target_filepath, 'wb') as target_f:
                            DirectoryWrapper._logger.info(f'Writing plain file: {target_filepath} ' +
                                                          f'with length {len(dr)}')
                            target_f.write(dr)
                else:
                    DirectoryWrapper._logger.warning(f'Non provenance file detected in directory {dirname}')

        if len(result_used) == 0:
            DirectoryWrapper._logger.warn(f'No provenance file detected in input directory {input_dirpath}')

        return result_used

    def plain2prov(self, used: Set, hashes: List, start: datetime, end: datetime, activity_id,
                   started_by=None):
        """
        Converts all non-prov files in a given directory into prov files. The prov files from an
        additional input directory are listed as used entities.
        """
        if started_by is not None:
            placeholder_activity = Activity(None, None, None, None, None)
            placeholder_activity._internal_id = started_by
        else:
            placeholder_activity = None
        provactivity = Activity(start_time=start, end_time=end, location=self.activity['location'],
                                label=self.activity['label'], means=self.activity['means'], used=used,
                                started_by=placeholder_activity
                                )
        if activity_id is not None:
            provactivity._internal_id = activity_id

        for h in hashes:
            rawprov = make_provstring(os.path.basename(h.name), Entity.FILE,
                                      self.__provagent, provactivity,
                                      h.hash
                                      )
            entityid = calculate_data_hash(rawprov)

            provfilename = '{}.prov'.format(entityid)

            provfile = os.path.join(os.path.dirname(h.name), provfilename)

            with open(provfile, 'wb') as target_f:
                target_f.write(rawprov)
                DirectoryWrapper._logger.info(f'Writing provenance file: {provfile} ' +
                                              f'with length {len(rawprov)}')

    def run_in(self, input_dirpath: str, start: str, end: str, activity_id: str = None, started_by: str = None):
        """
        """
        if input_dirpath is None:
            raise ValueError('Input dir path should not be None')
        DirectoryWrapper._logger.info('Creating plain files in directory: {}'.format(input_dirpath))
        self.prov2plain(input_dirpath)

    def run_out(self, input_dirpath: str, output_dirpath: str, start: str, end: str,
                activity_id: str = None, started_by: str = None):
        """
        """
        if output_dirpath is None:
            raise ValueError('Output dir path should not be None')
        DirectoryWrapper._logger.info('Creating prov files in directory: {}'.format(output_dirpath))

        used = set()
        if input_dirpath is not None:
            for dirname, dirnames, filenames in os.walk(input_dirpath):
                prov_files = [os.path.join(dirname, f) for f in filenames]
                for pf in prov_files:
                    if pf.endswith('.prov'):
                        with open(pf, 'rb') as f:
                            enthash = os.path.basename(pf).replace('.prov', '')
                            realhash = calculate_data_hash(f.read())
                            if enthash != realhash:
                                raise ValueError(f'Hash does not match file name for {pf}. Expecting {enthash} ' +
                                                 f'and got {realhash}')
                            used.add(enthash)
        hashes = []
        Hash = namedtuple('Hash', 'name hash')
        for dirname, dirnames, filenames in os.walk(output_dirpath):
            plain_files = [os.path.join(dirname, f) for f in filenames]
            for pf in plain_files:
                with open(pf, 'rb') as output_file:
                    datab = output_file.read()
                    hashes.append(Hash(pf, calculate_data_hash(datab)))

        self.plain2prov(used, hashes, dateutil.parser.parse(start),
                        dateutil.parser.parse(end), activity_id, started_by)


def create_activity_id():
    return ProvIdentifiableObject(generate_uuid=True).id


def main():
    usage_message = """
    %(prog)s [options]

    Example:

    python -m provtoolutils.directorywrapper --inputdir /home/testuser/test
    python -m provtoolutils.directorywrapper --configfile config.json --agentinfo agent.json \
           --inputdir /home/testuser/test --outputdir /home/testuser/test \
           --start YYYY-MM-DDThh:mm:ss --end YYYY-MM-DDThh:mm:ss
    """
    parser = argparse.ArgumentParser('Provenance directory wrapper', usage=usage_message,
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--configfile', help=textwrap.dedent(
        '''
            Static information about the used activity and agents.

            Example:
            #######

            {
               "agent": {
                   "type": "software",
                   "creator": "The author of the software",
                   "version": "The software version. This can also be a git commit, ...",
                   "label": "The software name",
                   "location": "The location, where more information about the software is available",
                   "acted_on_behalf_of": {
                       "given_name": "The persons given name",
                       "family_name": "The persons family name",
                       "type": "person"
                   }
               },
               "activity": {
                   "location": "Name of the machine, where the activity was performed on",
                   "label": "A short description/name of the activity",
                   "means": "A long description and explanation, why the activity was performed"
               }
            }
        '''
    ))
    parser.add_argument('--agentinfo', help=textwrap.dedent(
        '''
            Optional additional file with information about agents in json.

            The values listed in this file are additional to any agents mentioned in the config file.
            It is assummed, that the agents listed here are responsible for the agents mentioned in
            the config file.

            The information in this file is meant to be dynamic and changing with each call to the
            directorywrapper. This could be the case if for example multiple user (changing
            responsible) run the same tool (fixed agent) again and again.

            Example:
            ########

            {
               "agent": {
                   "given_name": "Frank",
                   "family_name": "Dressel",
                   "type": "person",
                   "acted_on_behalf_of": {
                       "name": "DLR",
                       "type": "organization"
                   }
               }
            }
        '''
    ))
    parser.add_argument('--createactivityid', action='store_true', help=textwrap.dedent(
        '''
            Start the programm in activity id generation mode. There will be no prov file generation
            or unpacking. It will generate an id, which can be later on be used for --started_by
            or --activity_id.
        '''
    ))
    parser.add_argument('--startedby', help=textwrap.dedent(
        '''
            Activity id of an overall workflow which started the process for which the files are currently used.
        '''
    ))
    parser.add_argument('--activityid', help=textwrap.dedent(
        '''
            Activity id to use.
        '''
    ))
    parser.add_argument('--inputdir')
    parser.add_argument('--outputdir')
    parser.add_argument('--start')
    parser.add_argument('--end')

    args = parser.parse_args()

    if args.createactivityid:
        print(create_activity_id())
        return

    if args.inputdir is not None and args.outputdir is None:
        pw = DirectoryWrapper(None, args.configfile)
        pw.run_in(args.inputdir, args.start, args.end)
        return

    if (args.outputdir is not None and args.start is not None and
            args.end is not None and args.configfile is not None):
        pw = DirectoryWrapper(args.agentinfo, args.configfile)
        pw.run_out(args.inputdir, args.outputdir, args.start, args.end,
                   args.activityid if 'activityid' in args else None,
                   args.startedby if 'startedby' in args else None)
        return

    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':  # pragma: no cover
    main()
