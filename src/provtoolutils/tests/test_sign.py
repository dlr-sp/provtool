import json
import pytest
import os
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

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


def test_integration(reference_dir):

    provfile = os.path.join(reference_dir, '29b2006eddfac9a26f4c5d98d63ba14c3096b2b461f9c8364b26c3670ab00c23.prov')

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_file = os.path.join(reference_dir, 'priv.pem')
    public_key_file = os.path.join(reference_dir, 'pub.pem')
    with open(private_key_file, 'wb') as priv:
        priv.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                             format=serialization.PrivateFormat.TraditionalOpenSSL,
                                             encryption_algorithm=serialization.NoEncryption()))

    assert len(os.listdir(reference_dir)) == 2

    return_code = subprocess.call(
        [sys.executable, '-m', 'provtoolutils.sign', '--provfile', provfile, '--private', private_key_file, '--familyname',
         'Mustermensch', '--givenname', 'Maxi', '--timestampserver', 'http://zeitstempel.dfn.de'])
    assert return_code == 0

    files = os.listdir(reference_dir)
    assert len(files) == 5

    signedprov = [f for f in files if f != '29b2006eddfac9a26f4c5d98d63ba14c3096b2b461f9c8364b26c3670ab00c23.prov' and f.endswith('.prov')][0]
    with open(os.path.join(reference_dir, signedprov)) as spf:
        js = json.loads(spf.read())
        with open(os.path.join(reference_dir, js['signature']['provtool:signature']), 'rb') as s, open(provfile, 'rb') as p:
            signature = s.read()
            message = p.read()

            private_key.public_key().verify(
                    signature,
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                        ),
                    hashes.SHA256()
                    )
