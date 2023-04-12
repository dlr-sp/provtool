import os
import pytest
import tempfile

from distutils import dir_util
from pathlib import Path
from provtoolutils.constants import model_encoding

from localcontainerreader.reader import search, read_provanddata

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

def test_read_provanddata(reference_dir):
    data = 'Hello World'

    pr, dr, err = read_provanddata({'directory': reference_dir}, 'fd14ee953e58d379989eed4881a0e125392fb1f9f4d39faea99445fe2e472272')
    assert err == False
    assert dr.decode(model_encoding) == data

def test_missing_datafile(reference_dir):
    pr, dr, err = read_provanddata({'directory': reference_dir}, '3b31873b5fd04856dc0a4fe2d84e818b8c2e36e38018e7985fc565bf6b771498')
    assert err == True

def test_read_provanddata_file(reference_dir):
    data = 'hurgs\n'

    pr, dr, err = read_provanddata({'directory': reference_dir}, '582b990865a3f5ca9108f78afcc57a81035b74f0789d0a8d00e76be6daa7a129')
    assert err == False
    assert dr.decode(model_encoding) == data

def test_search(reference_dir):
    location = search({'directory': reference_dir}, 'test.txt')
    assert len(location) == 1
    assert os.path.join(reference_dir, 'sub1',
                        '582b990865a3f5ca9108f78afcc57a81035b74f0789d0a8d00e76be6daa7a129.prov') in location
