import datetime
import dateutil.parser
import json
import jsonschema
import os
import pytest
import re
import sys
import tempfile

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from git import Repo

from provtoolutils.constants import model_encoding, prov_schema
from provtoolutils.model import make_provstring, Activity, Entity, Person
from provtoolutils.standalone import Standalone
from provtoolutils.utilities import calculate_data_hash

data = 'Hello World'
testfile_name = 'test.txt'

discovered_plugins = entry_points(group='provtoolutils.reader')
read_provanddata = getattr(discovered_plugins['file'].load(), 'read_provanddata')


def create_mock_input(answers):
    def mock_input(prompt):
        for k, v in answers.items():
            if re.match('.*{}.*'.format(k), prompt):
                return v.pop()

    return mock_input


def default_answers():
    return {
        'entity_path': ['replace.me'],
        'author_family_name': ['Mustermann'],
        'author_given_name': ['Max'],
        'more authors': ['n'],
        'activity_location': ['here'],
        'activity_label': ['Activity'],
        'activity_means': ['This activity is used for testing purposes'],
        'activity_time': ['2019-09-02T10:14:00+00:00'],
        'Are there used entities': ['n'],
        'information correct': ['y']
    }


def _run_standalone_first(filedir, mocker, sa):
    entity_path = os.path.join(filedir, testfile_name)
    with open(entity_path, 'w') as f:
        f.write(data)
    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    assert not os.path.exists(mapping_file)
    answers = default_answers()
    answers['entity_path'] = [entity_path]

    mocker.patch('builtins.input', create_mock_input(answers))
    sa.run()
    return entity_path, mapping_file


def _run_standalone_repeated(mocker, sa):
    answers_repeated = default_answers()
    answers_repeated['entity_path'] = ['y']
    answers_repeated['author_family_name'] = ['y']
    answers_repeated['author_given_name'] = ['y']
    answers_repeated['more authors'] = ['n']
    answers_repeated['activity_location'] = ['y']
    answers_repeated['activity_label'] = ['y']
    answers_repeated['activity_means'] = ['y']
    answers_repeated['activity_time'] = ['y']
    answers_repeated['information correct'] = ['y']

    mocker.patch('builtins.input', create_mock_input(answers_repeated))
    sa.run()


@pytest.fixture
def filedir():
    with tempfile.TemporaryDirectory() as d:
        yield d


'''
    Unit tests following
'''

def test_yn_feedback(mocker):
    wrong = 0

    def mock_input(prompt):
        nonlocal wrong

        if 'Return y' in prompt:
            return 'y'
        if 'Return n' in prompt:
            return 'n'
        if 'Repeat y' in prompt and wrong == 0:
            wrong = wrong + 1
            return 'tralala'
        if 'Repeat y' in prompt and wrong > 0:
            return 'y'

    mocker.patch('builtins.input', mock_input)
    assert Standalone.yn_feedback('Return y') == 'y'
    mocker.patch('builtins.input', mock_input)
    assert Standalone.yn_feedback('Return n') == 'n'
    mocker.patch('builtins.input', mock_input)
    assert Standalone.yn_feedback('Return y') == 'y'
    mocker.patch('builtins.input', mock_input)
    assert Standalone.yn_feedback('Return n') == 'n'
    mocker.patch('builtins.input', mock_input)
    assert Standalone.yn_feedback('Repeat y') == 'y'


def test_db_creation():
    sa = Standalone(db=':memory:')
    assert sa.conn.execute('select * from provtool').fetchall()
    assert len(sa.conn.execute('select * from provtool').fetchall()) > 0


def test_write_prov_file(filedir):
    entity_path = os.path.join(filedir, 'test.txt')
    with open(entity_path, 'w') as f:
        f.write(data)

    sa = Standalone(db=':memory:')
    starttime = datetime.datetime.now(datetime.timezone.utc)
    sa.write_prov_file(starttime, 'location', 'label', 'means', [], entity_path, Person('Mäx', 'Müstermann'))

    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    assert os.path.exists(mapping_file)
    assert os.path.exists(os.path.join(filedir, calculate_data_hash(data.encode(model_encoding))))

    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err =read_provanddata({'directory': os.path.dirname(resultfile)}, 
                                       os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        assert dr.decode(model_encoding) == data

        prov = pr.decode(model_encoding)
        assert re.match('.*Müstermann.*', prov)

'''
    Integration tests following
'''


def test_file_creation_and_content(filedir, mocker):
    sa = Standalone(db=':memory:')
    entity_path, mapping_file = _run_standalone_first(filedir, mocker, sa)

    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))

def test_file_usage(filedir, mocker):
    entity_path = os.path.join(filedir, 'test.txt')
    with open(entity_path, 'w') as f:
        f.write(data)

    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    assert not os.path.exists(mapping_file)

    answers = default_answers()
    answers['entity_path'] = [entity_path]
    answers['Are there used entities'] = ['y', 'n']
    answers['entity_id'] = ['123456789']
    answers['information correct'] = ['y']

    mocker.patch('builtins.input', create_mock_input(answers))
    sa = Standalone(db=':memory:')
    sa.run()

    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err =read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        assert dr.decode(model_encoding) == data
        assert 'used' in pr.decode(model_encoding)

def test_file_creation_multiple_authors(filedir, mocker):
    entity_path = os.path.join(filedir, 'test.txt')
    with open(entity_path, 'w') as f:
        f.write(data)

    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    assert not os.path.exists(mapping_file)

    answers = default_answers()
    answers['entity_path'] = [entity_path]
    answers['author_family_name'] = ['Mustermann2', 'n', 'Mustermann']
    answers['author_given_name'] = ['Max2', 'n', 'Max']
    answers['more authors'] = ['n', 'y']

    mocker.patch('builtins.input', create_mock_input(answers))
    sa = Standalone(db=':memory:')
    sa.run()

    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err = read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        assert dr.decode(model_encoding) == data

        js = json.loads(pr.decode(model_encoding))
        assert len(js['agent']) == 2
        assert len(js['actedOnBehalfOf']) == 1

def test_input_remembering(filedir, mocker):
    sa = Standalone(db=':memory:')
    entity_path, mapping_file = _run_standalone_first(filedir, mocker, sa)

    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        assert os.path.exists(resultfile)

        os.remove(resultfile)

    os.remove(mapping_file)
    _run_standalone_repeated(mocker, sa)

    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err = read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        dr.decode(model_encoding) == data

def test_same_id(filedir, mocker):
    sa = Standalone(db=':memory:')

    rawdatafile_name = os.path.join(filedir, calculate_data_hash(data.encode(model_encoding)))
    assert not os.path.exists(os.path.join(filedir, testfile_name))
    assert not os.path.exists(rawdatafile_name)

    entity_path, mapping_file = _run_standalone_first(filedir, mocker, sa)

    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        filename_1 = os.path.join(filedir, mappings[entity_path])
        assert os.path.exists(filename_1)
        assert os.path.exists(rawdatafile_name)

        os.remove(filename_1)
        os.remove(rawdatafile_name)

    os.remove(mapping_file)
    _run_standalone_repeated(mocker, sa)

    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        filename_2 = os.path.join(filedir, mappings[entity_path])
        assert os.path.exists(filename_2)
        assert os.path.exists(rawdatafile_name)

        os.remove(filename_2)
        os.remove(rawdatafile_name)

    assert len(filename_1) > 0
    assert len(filename_2) > 0
    assert filename_1 == filename_2

def test_repository_mode(filedir, mocker):
    entity_path = os.path.join(filedir, 'test.txt')
    with open(entity_path, 'w') as f:
        f.write(data)

    repo = Repo.init(filedir)
    repo.config_writer().set_value("user", "name", "Max Müstermann").release()
    repo.config_writer().set_value("user", "email", "max.müstermann@musterstadt.de").release()

    repo.index.add(entity_path)
    cm = repo.index.commit("Initial commit for testing purpose")

    sa = Standalone(db=':memory:')
    sa.run_repo(filedir, entity_path)

    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    assert os.path.exists(mapping_file)
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        assert entity_path in mappings

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err = read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        assert dr.decode(model_encoding) == data

        js = json.loads(pr.decode(model_encoding))
        jsonschema.validate(js, prov_schema)

        ag = next(iter(js['agent'].values()))

        assert ag['person:familyName'] == 'Müstermann'
        assert ag['person:givenName'] == 'Max'
        assert ag['prov:label'] == 'Max Müstermann'
        assert ag['prov:type'] == 'prov:Person'

        assert len(js['activity']) == 1
        ac = next(iter(js['activity'].values()))
        assert ac['prov:label'] == f'Git commit {cm}'
        assert dateutil.parser.parse(ac['prov:endTime']) > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=-5)
        assert dateutil.parser.parse(ac['prov:endTime']) > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=-5)

def test_repository_mode_additional_comment(filedir, mocker):
    entity_path = os.path.join(filedir, 'test.txt')
    with open(entity_path, 'w') as f:
        f.write(data)

    repo = Repo.init(filedir)
    repo.config_writer().set_value("user", "name", "Max Müstermann").release()
    repo.config_writer().set_value("user", "email", "max.müstermann@musterstadt.de").release()

    repo.index.add(entity_path)
    cm = repo.index.commit("Initial commit for testing purpose")

    sa = Standalone(db=':memory:')
    sa.run_repo(filedir, entity_path, 'Testactivity')

    mapping_file = os.path.join(filedir, 'provtool_filemapping.txt')
    with open(mapping_file, 'r') as f:
        mappings = {}
        for l in f.readlines():
            s = l.split('=')
            mappings[s[0].strip()] = s[1].strip()

        resultfile = os.path.join(filedir, mappings[entity_path])
        pr, dr, err = read_provanddata({'directory': os.path.dirname(resultfile)}, os.path.basename(resultfile).replace('.prov', ''))
        assert not err
        assert dr.decode(model_encoding) == data

        js = json.loads(pr.decode(model_encoding))
        jsonschema.validate(js, prov_schema)

        ac = next(iter(js['activity'].values()))
        assert ac['prov:label'] == f'Git commit {cm}. Testactivity'
