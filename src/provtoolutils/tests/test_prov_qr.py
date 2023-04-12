import hashlib
import os
import pytest
import subprocess
import sys
import tempfile

from distutils import dir_util
from pathlib import Path
from provtoolutils.prov_qr import qr
from subprocess import PIPE

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
def reference_image(reference_dir):
    return os.path.join(reference_dir, 'test.png')

def test_qr(reference_dir, reference_image):
    tar_path = os.path.join(reference_dir, 'test.png')
    qr(os.path.join(reference_dir, '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'), tar_path)

    with open(reference_image, 'rb') as ref, open(tar_path, 'rb') as tar:
        digest = hashlib.sha256()
        digest.update(ref.read())
        ref_hash = digest.hexdigest()

        digest = hashlib.sha256()
        digest.update(tar.read())
        tar_hash = digest.hexdigest()
        
        assert ref_hash == tar_hash

def test_integration(reference_dir, reference_image):
    integrationtest_image = os.path.join(reference_dir, 'test_integration.png')
    tar_path = os.path.join(reference_dir, 'test.png')

    assert not os.path.exists(integrationtest_image)

    process = subprocess.run([sys.executable,
            '-m',
            'provtoolutils.prov_qr',
            '--provfile',
            os.path.join(reference_dir, '751e9fe9fa9960259fb082a57d39461878d602b77eedd6bb5bdcaa1828b64034.prov'),
            '--imagefile',
            integrationtest_image
        ], stdout=PIPE)
    
    assert process.returncode == 0
    assert os.path.exists(integrationtest_image)

    with open(reference_image, 'rb') as ref, open(tar_path, 'rb') as tar:
        digest = hashlib.sha256()
        digest.update(ref.read())
        ref_hash = digest.hexdigest()

        digest = hashlib.sha256()
        digest.update(tar.read())
        tar_hash = digest.hexdigest()
        
        assert ref_hash == tar_hash
