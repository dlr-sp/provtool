import os
import pytest
import re
import subprocess
import tempfile

from distutils import dir_util
from pathlib import Path


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


def test_main_single_entity(reference_dir):
    htmlreportfile_path = os.path.join(reference_dir, 'validation_report.html')
    csvreportfile_path = os.path.join(reference_dir, 'validation_report.csv')
    configfile_path = os.path.join(reference_dir, 'validation_config.ini')

    assert not os.path.exists(htmlreportfile_path)

    with open(configfile_path, 'w') as config_file:
        config_file.write('[handlers]\nlocal=provtoolval.localdatalocation.LocalDataLocation#{}'.format(reference_dir))

    for rfp in [htmlreportfile_path, csvreportfile_path]:
        subprocess.call([
            'python',
            '-m', 'provtoolval.main',
            '--filelocation', reference_dir,
            '--target', '52da7d6cfd7eec1fee8b40f7311484d36a186eca32a1fd1a491751d0abd40b29',
            '--reportfile', rfp
        ])

        assert os.path.exists(rfp)

        with open(rfp, 'r') as report_file:
            content = report_file.read()
            assert not re.match('.*be5a59cc1407cb1827220effb586e9006b61593594491d9f0e7b84cf79880619.*', content, re.DOTALL)


def test_incomplete_arguments(reference_dir):
    rc = subprocess.call([
        'python',
        '-m', 'provtoolval.main',
        '--reportfile', 'test.html'
    ])

    assert rc != 0

    rc = subprocess.call([
        'python',
        '-m', 'provtoolval.main',
        '--filelocation', reference_dir,
    ])

    assert rc != 0
