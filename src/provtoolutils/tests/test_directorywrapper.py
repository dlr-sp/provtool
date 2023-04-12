import datetime
import glob
import json
import jsonschema
import os
import pytest
import re
import shutil
import subprocess
import sys
import tempfile

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from distutils import dir_util
from pathlib import Path
from subprocess import PIPE

from collections import namedtuple

from provtoolutils.constants import prov_schema, model_encoding
from provtoolutils.directorywrapper import DirectoryWrapper
from provtoolutils.utilities import calculate_data_hash
from provtoolutils.model import make_provstring, ActingSoftware, Activity, Entity, Person

teststring1 = 'Ijon Tichy ist ein allseits bekannter Raumfahrer. Immer an Bord seiner Rakete: Seine '
teststring2 = 'Ijon Tichy ist ein allseits bekannter Raumfahrer. Immer an Bord seiner Rakete: Seine analoge Halluzinelle'

discovered_plugins = entry_points(group='provtoolutils.reader')
read_provanddata = getattr(discovered_plugins['file'].load(), 'read_provanddata')

Hash = namedtuple('Hash', 'name hash')

@pytest.fixture
def ref_tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.fixture
def reference_dir(ref_tmpdir, request):
    filename = request.module.__file__
    data_dir = Path(filename).with_suffix('')

    if os.path.exists(data_dir):
        dir_util.copy_tree(data_dir, str(ref_tmpdir))

    return ref_tmpdir

@pytest.fixture
def entity_name():
    return 'test.txt'

@pytest.fixture
def base_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d

@pytest.fixture
def plain_input_filepath(base_dir, entity_name):
    return os.path.join(base_dir, entity_name)

@pytest.fixture
def log_filepath(base_dir):
    return os.path.join(base_dir, 'DirectoryWrapper.log')

@pytest.fixture
def program_parameterfilename(base_dir):
    return 'parameters.ini'

@pytest.fixture
def prov_input_filepath(base_dir, entity_name):

    start = datetime.datetime(2019, 8, 16, 12, 31, 14, tzinfo=datetime.timezone.utc)
    data = teststring1.encode('utf-8')
    end = datetime.datetime(2019, 8, 16, 14, 31, 14, tzinfo=datetime.timezone.utc)

    activity_location = ''
    activity_label = 'Generate a test data file'
    activity_means = 'A file with known content is needed for repeated automated tests. Such a file is generated.'

    responsible_given_name = 'Max'
    responsible_family_name = 'Mustermann'

    software_creator = 'Max Mustermann'
    software_version = '0.0.1'
    software_label = 'create_file_for_tests.py'
    software_location = ''

    activity = Activity(
        start_time=start,
        end_time=end,
        location=activity_location,
        label=activity_label,
        means=activity_means
    )
    responsible = Person(
        given_name=responsible_given_name,
        family_name=responsible_family_name
    )
    script = ActingSoftware(
        acted_on_behalf_of=responsible,
        creator=software_creator,
        version=software_version,
        label=software_label,
        location=software_location
    )

    data_hash = calculate_data_hash(data)
    rawprov = make_provstring(entity_name, Entity.FILE, script, activity, data_hash)
    entityid = calculate_data_hash(rawprov)

    filename = os.path.join(base_dir, '{}.prov'.format(entityid))
    with open(filename, 'wb') as out_file:
        out_file.write(rawprov)
    with open(os.path.join(base_dir, calculate_data_hash(data)), 'wb') as out_file:
        out_file.write(data)

    return filename


@pytest.fixture
def config_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "type": "software",\n'
            '       "creator": "Max Mustermann",\n'
            '       "version": "-",\n'
            '       "label": "Test script for automatic tests of DirectoryWrapper",\n'
            '       "location": "-",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Max",\n'
            '           "family_name": "Mustermann",\n'
            '           "type": "person"\n'
            '       }\n'
            '   },\n'
            '   "activity": {\n'
            '       "location": "The current work station",\n'
            '       "label": "Automatic tests for DirectoryWrapper",\n'
            '       "means": "The DirectoryWrapper takes existing non provenance aware programms and adds provenance awareness ' +\
                        'to it without modification of the original program. This involves a lot of file handling and parameter ' +\
                        'passing, which needs to be tested automatically."\n'
            '   }\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def brokenconfig_agent_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agehnt": {\n'
            '       "type": "software",\n'
            '       "creator": "Max Mustermann",\n'
            '       "version": "-",\n'
            '       "label": "Test script for automatic tests of DirectoryWrapper",\n'
            '       "location": "-",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Max",\n'
            '           "family_name": "Mustermann",\n'
            '           "type": "person"\n'
            '       }\n'
            '   },\n'
            '   "activity": {\n'
            '       "location": "The current work station",\n'
            '       "label": "Automatic tests for DirectoryWrapper",\n'
            '       "means": "The DirectoryWrapper takes existing non provenance aware programms and adds provenance awareness ' +\
                        'to it without modification of the original program. This involves a lot of file handling and parameter' +\
                        'passing, which needs to be tested automatically."\n'
            '   }\n'
            '}'
        ])
    return config_filepath

@pytest.fixture
def brokenconfig_activity_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "type": "software",\n'
            '       "creator": "Max Mustermann",\n'
            '       "version": "-",\n'
            '       "label": "Test script for automatic tests of DirectoryWrapper",\n'
            '       "location": "-",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Max",\n'
            '           "family_name": "Mustermann",\n'
            '           "type": "person"\n'
            '       }\n'
            '   },\n'
            '   "actihvity": {\n'
            '       "location": "The current work station",\n'
            '       "label": "Automatic tests for DirectoryWrapper",\n'
            '       "means": "The DirectoryWrapper takes existing non provenance aware programms and adds provenance awareness ' +\
                        'to it without modification of the original program. This involves a lot of file handling and parameter' +\
                        'passing, which needs to be tested automatically."\n'
            '   }\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def config_without_actingsoftware_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "type": "person",\n'
            '       "given_name": "Nadine",\n'
            '       "family_name": "Mustermann",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Max",\n'
            '           "family_name": "Mustermann",\n'
            '           "type": "person"\n'
            '       }\n'
            '   },\n'
            '   "activity": {\n'
            '       "location": "The current work station",\n'
            '       "label": "Automatic tests for DirectoryWrapper",\n'
            '       "means": "The DirectoryWrapper takes existing non provenance aware programms and adds provenance awareness ' +\
                        'to it without modification of the original program. This involves a lot of file handling and parameter' +\
                        'passing, which needs to be tested automatically."\n'
            '   }\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def config_without_agent(base_dir):
    config_filepath = os.path.join(base_dir, 'config.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "activity": {\n'
            '       "location": "The current work station",\n'
            '       "label": "Automatic tests for DirectoryWrapper",\n'
            '       "means": "The DirectoryWrapper takes existing non provenance aware programms and adds provenance awareness ' +\
                        'to it without modification of the original program. This involves a lot of file handling and parameter ' +\
                        'passing, which needs to be tested automatically."\n'
            '   }\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def agentinfo_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'agent.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "label": "provtool",\n'
            '       "version": "0.1.13",\n'
            '       "creator": "fd",\n'
            '       "location": "Somewhere",\n'
            '       "type": "software",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Frank",\n'
            '           "family_name": "Dressel",\n'
            '           "type": "person",\n'
            '           "acted_on_behalf_of": {\n'
            '               "label": "DLR",\n'
            '               "type": "organization"\n'
            '           }\n'
            '       }\n'
            '   }\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def agentinfo_extended_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'agent.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "label": "provtool",\n'
            '       "version": "0.1.13",\n'
            '       "creator": "fd",\n'
            '       "location": "Somewhere",\n'
            '       "type": "software",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Frank",\n'
            '           "family_name": "Dressel",\n'
            '           "type": "person",\n'
            '           "acted_on_behalf_of": {\n'
            '               "label": "DLR",\n'
            '               "type": "organization"\n'
            '           }\n'
            '       }\n'
            '   },\n'
            '   "schnurps": {}\n'
            '}'
        ])
    return config_filepath


@pytest.fixture
def corrupt_agentinfo_filepath(base_dir):
    config_filepath = os.path.join(base_dir, 'agent.json')
    with open(config_filepath, 'w') as f:
        f.writelines([
            '{\n'
            '   "agent": {\n'
            '       "label": "provtool",\n'
            '       "version": 0.1.13",\n'
            '       "creator": "fd",\n'
            '       "location": "Somewhere",\n'
            '       "type": "software",\n'
            '       "acted_on_behalf_of": {\n'
            '           "given_name": "Frank",\n'
            '           "family_name": "Dressel",\n'
            '           "type": "person",\n'
            '           "acted_on_behalf_of": {\n'
            '               "label": "DLR",\n'
            '               "type": "organization"\n'
            '           }\n'
            '       }\n'
            '   }\n'
            '}'
        ])
    return config_filepath


def test_input(config_filepath, prov_input_filepath, plain_input_filepath, base_dir, entity_name):

    assert os.path.isfile(prov_input_filepath)
    assert not os.path.isfile(plain_input_filepath)

    DirectoryWrapper(None, config_filepath).run_in(os.path.dirname(prov_input_filepath), None, None)
    # The input prov file should be unwrapped.
    assert os.path.isfile(plain_input_filepath)
    with open(plain_input_filepath, 'r') as f:
        assert f.read() == teststring1


def test_multiple_output(config_filepath, prov_input_filepath, base_dir, log_filepath):
    assert os.path.isfile(prov_input_filepath)

    out_dir = os.path.join(base_dir, 'test_multiple_output')
    os.mkdir(out_dir)
    open(os.path.join(out_dir, 't1'), 'a').close()
    open(os.path.join(out_dir, 't2'), 'a').close()

    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%y-%m-%dT%H:%M:%S%z')
    DirectoryWrapper(None, config_filepath).run_out(os.path.dirname(prov_input_filepath), out_dir, startend, startend)

    prov_files = [f for f in os.listdir(out_dir) if f.endswith('.prov')]
    assert len(prov_files) == 2
    labels = []

    for pf in prov_files:
        with open(os.path.join(out_dir, pf)) as f:
            data = f.read()

            prov = json.loads(re.sub('^[^{]+', '', re.sub('}}}.*', '}}}', data)))
            labels.append(next(iter(prov['entity'].values()))['prov:label'])

    assert 't1' in labels
    assert 't2' in labels


def test_program_start_with_missing_agent(brokenconfig_agent_filepath):
    with pytest.raises(RuntimeError, match='.*o agent defined.*'):
        DirectoryWrapper(None, brokenconfig_agent_filepath)


def test_program_start_with_missing_activity(brokenconfig_activity_filepath):
    with pytest.raises(RuntimeError, match='.*ailed to validate config.*'):
        DirectoryWrapper(None, brokenconfig_activity_filepath)


#def test_program_start_without_actingsoftware(config_without_actingsoftware_filepath):
#    with pytest.raises(RuntimeError, match='.*ActingSoftware.*'):
#        DirectoryWrapper(None, config_without_actingsoftware_filepath)


def test_integration_unpacking(reference_dir, base_dir, config_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    assert not os.path.exists(os.path.join(indir, 'testfile.txt'))
    return_code = subprocess.call([sys.executable, '-m', 'provtoolutils.directorywrapper', '--inputdir', indir])
    assert return_code == 0
    assert os.path.exists(os.path.join(indir, 'testfile2.txt'))


def test_integration_config_file_with_agent(reference_dir, base_dir, config_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()
    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call([sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--inputdir', indir, '--outputdir', outdir, '--start', startend, '--end', startend])
    assert return_code == 0
    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))
    prov = json.loads(pr.decode(model_encoding))
    assert len(prov['agent']) == 2
    assert len(prov['actedOnBehalfOf']) == 1


def test_integration_config_file_without_agent_with_agentinfo_file(reference_dir, base_dir, config_without_agent, agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()
    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')

    return_code = subprocess.call([sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_without_agent, '--agentinfo', agentinfo_filepath, '--inputdir', indir, '--outputdir', outdir, '--start', startend, '--end', startend])
    assert return_code == 0
    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))

    assert 'actedOnBehalfOf' in pr.decode(model_encoding)

def test_integration_config_file_without_agent_with_corrupt_agentinfo_file(reference_dir, base_dir, config_without_agent, corrupt_agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()
    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')

    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_without_agent,
         '--agentinfo', corrupt_agentinfo_filepath, '--inputdir', indir, '--outputdir', outdir, '--start', startend,
         '--end', startend])
    assert return_code == 1


def test_integration_config_file_with_agent_and_agentinfo_file(reference_dir, base_dir, config_filepath, agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()
    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')

    return_code = subprocess.call([sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--agentinfo', agentinfo_filepath, '--inputdir', indir, '--outputdir', outdir, '--start', startend, '--end', startend])
    assert return_code == 0

    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))
    prov = json.loads(pr.decode(model_encoding))
    assert len(prov['agent']) == 5
    assert len(prov['actedOnBehalfOf']) == 4


def test_integration_activity_id_creation(base_dir, config_filepath, agentinfo_filepath):
    process = subprocess.run([sys.executable, '-m', 'provtoolutils.directorywrapper', '--createactivityid'], stdout=PIPE)

    assert re.match(r'^[a-f0-9]+$', process.stdout.decode('utf-8').replace('\r', '').replace('\n', ''))
    assert process.returncode == 0


def test_integration_started_by(reference_dir, base_dir, config_filepath, agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()

    test_act_id = 'abcdefghijklmnopqrstuvwxyz'

    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--inputdir', indir,
         '--outputdir', outdir, '--start', startend, '--end', startend, '--startedby', test_act_id])
    assert return_code == 0
    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))
    prov = json.loads(pr.decode(model_encoding))

    wsb = next(iter(prov['wasStartedBy'].values()))
    assert wsb['prov:starter'] == test_act_id


def test_integration_withoutstarted_by(reference_dir, base_dir, config_filepath, agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()

    test_act_id = 'abcdefghijklmnopqrstuvwxyz'

    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--inputdir', indir,
         '--outputdir', outdir, '--start', startend, '--end', startend])
    assert return_code == 0
    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))
    prov = json.loads(pr.decode(model_encoding))

    assert not 'wasStartedBy' in prov


def test_integration_fixed_activity_id(reference_dir, base_dir, config_filepath, agentinfo_filepath):
    indir = os.path.join(base_dir, 'in')
    os.mkdir(indir)
    shutil.copy(os.path.join(reference_dir, 'integration', '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), indir)
    shutil.copy(os.path.join(reference_dir, 'integration', 'aa1db5c660d3d1f3f4f9361b9848694300929be94b74c84452a87420c59e5df9'), indir)
    outdir = os.path.join(base_dir, 'out')
    os.mkdir(outdir)
    open(os.path.join(outdir, 'result.txt'), 'w').close()

    test_act_id = 'abcdefghijklmnopqrstuvwxyz'

    assert len([f for f in os.listdir(outdir) if f.endswith('.prov')]) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--inputdir', indir,
         '--outputdir', outdir, '--start', startend, '--end', startend, '--activityid', test_act_id])
    assert return_code == 0
    prov_files = [f for f in os.listdir(outdir) if f.endswith('.prov')]
    assert len(prov_files) == 1

    pr, dr, err = read_provanddata({'directory': outdir}, prov_files[0].replace('.prov', ''))
    prov = json.loads(pr.decode(model_encoding))

    assert test_act_id in prov['activity']


def test_integration_directorystructure(reference_dir, config_filepath):
    outdir = os.path.join(reference_dir, 'plain2prov')
    indir = os.path.join(reference_dir, 'plain2prov', 'in')
    os.mkdir(indir)

    assert len(glob.glob(outdir + '/**/*.prov', recursive=True)) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath, '--inputdir', indir,
         '--outputdir', outdir, '--start', startend, '--end', startend, '--activityid', 'act_id'])
    assert return_code == 0

    assert len(glob.glob(outdir + '/**/*.prov', recursive=True)) == 3
    assert len(glob.glob(os.path.join(outdir, 'sub1') + '/*.prov')) == 1
    assert len(glob.glob(os.path.join(outdir, 'sub1', 'sub11') + '/*.prov')) == 1
    assert len(glob.glob(os.path.join(outdir, 'sub2') + '/*.prov')) == 1

def test_integration_missing_input(reference_dir, config_filepath):
    outdir = os.path.join(reference_dir, 'plain2prov')

    assert len(glob.glob(outdir + '/**/*.prov', recursive=True)) == 0
    startend = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), '%Y-%m-%dT%H:%M:%S%z')
    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.directorywrapper', '--configfile', config_filepath,
         '--outputdir', outdir, '--start', startend, '--end', startend, '--activityid', 'act_id'])
    assert return_code == 0

    assert len(glob.glob(outdir + '/**/*.prov', recursive=True)) == 3
    assert len(glob.glob(os.path.join(outdir, 'sub1') + '/*.prov')) == 1
    assert len(glob.glob(os.path.join(outdir, 'sub1', 'sub11') + '/*.prov')) == 1
    assert len(glob.glob(os.path.join(outdir, 'sub2') + '/*.prov')) == 1

def test_plain2prov(config_filepath, reference_dir):
    with tempfile.TemporaryDirectory() as temp_d:
        with open(os.path.join(temp_d, 'test.txt'), 'w') as test_file:
            test_file.write('Hallo')

        dw = DirectoryWrapper(None, config_filepath)
        used = set()
        for dirname, dirnames, filenames in os.walk(os.path.join(reference_dir, 'subdir')):
            [used.add(pf.replace('.prov', '')) for pf in filenames if pf.endswith('.prov')]
        hashes = []
        for dirname, dirnames, filenames in os.walk(temp_d):
            for fn in filenames:
                absfp = os.path.join(dirname, fn)
                with open(absfp, 'rb') as f:
                    hashes.append(Hash(absfp, calculate_data_hash(f.read())))
        dw.plain2prov(used, hashes, datetime.datetime.now(datetime.timezone.utc), datetime.datetime.now(datetime.timezone.utc), 'testactivity')

        dir_list = [p for p in os.listdir(temp_d) if p.endswith('.prov')]
        assert len(dir_list) == 1

        pr, dr, err = read_provanddata({'directory': temp_d}, dir_list[0].replace('.prov', ''))
        prov = json.loads(pr.decode(model_encoding))
        jsonschema.validate(prov, prov_schema)

        assert os.path.basename(dir_list[0].replace('.prov', '')) == calculate_data_hash(pr) 

def test_prov2plain(config_filepath, reference_dir):
    testfiledirpath = os.path.join(reference_dir, 'prov2plain')
    dw = DirectoryWrapper(None, None)
    plained = dw.prov2plain(testfiledirpath)

    assert len(plained) == 3

    corruptfiledirpath = os.path.join(reference_dir, 'corrupt')
    dw = DirectoryWrapper(None, None)
    with pytest.raises(Exception):
        used = dw.prov2plain(corruptfiledirpath)

def test_prov2plain_duplicateexception(config_filepath, reference_dir):
    duplicates_filedirpath = os.path.join(reference_dir, 'duplicates')
    dw = DirectoryWrapper(None, None)
    with pytest.raises(Exception):
        used = dw.prov2plain(duplicates_filedirpath)

def test_parse_agentinfo(agentinfo_filepath):
    with open(agentinfo_filepath, 'r', encoding='utf-8') as f:
        parsed = DirectoryWrapper._parse_agentinfo(f.read())

        assert type(parsed) == ActingSoftware
        assert parsed.label == 'provtool'

        p = parsed.acted_on_behalf_of
        assert p is not None
        assert type(p) == Person
        assert p.family_name == 'Dressel'

        o = p.acted_on_behalf_of
        assert o is not None
        assert o.name == 'DLR'


def test_parse_agentinfo_extended_file(agentinfo_extended_filepath):
    with open(agentinfo_extended_filepath, 'r', encoding='utf-8') as f:
        parsed = DirectoryWrapper._parse_agentinfo(f.read())

        assert type(parsed) == ActingSoftware
        assert parsed.label == 'provtool'

        p = parsed.acted_on_behalf_of
        assert p is not None
        assert type(p) == Person
        assert p.family_name == 'Dressel'

        o = p.acted_on_behalf_of
        assert o is not None
        assert o.name == 'DLR'
