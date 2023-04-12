import os
import pytest
import subprocess
import sys
import tempfile

from distutils import dir_util
from pathlib import Path
from subprocess import PIPE


@pytest.fixture
def base_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d
        

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


def test_integration_searchdir(base_dir, reference_dir):
    p = subprocess.run(
        [sys.executable, '-m', 'provtoolutils.search', '--entityname', 'testfile2.txt', '--searchdir', reference_dir], cwd=base_dir, stdout=PIPE)

    assert p.returncode == 0
    assert p.stdout.strip().decode() == os.path.join(reference_dir, '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov')
