import json
import os
import pytest
import requests_mock
import tempfile
import shutil
import sys

from cryptography.hazmat.primitives.asymmetric import rsa
from distutils import dir_util
from pathlib import Path

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from provtoolutils.constants import model_encoding

from provtoolutils.utilities import calculate_data_hash, calculate_sign_hash, convert_rawprov2containerprov, sign

discovered_plugins = entry_points(group='provtoolutils.reader')
read_provanddata = getattr(discovered_plugins['file'].load(), 'read_provanddata')

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

def test_calculate_data_hash():
    datahash = calculate_data_hash('Es klapperten die Klapperschlangen, bis ihre Klappern schlapper klangen'.encode('utf-8'))
    assert datahash == '4f751758ac4e03c2d6c57eeb97428a32e95bbabc8500bc26684ef56a5508fe52'

def test_calculate_sign_hash(reference_dir):
    # Check with unmodified.
    entityid = '29b2006eddfac9a26f4c5d98d63ba14c3096b2b461f9c8364b26c3670ab00c23'
    rawprov, dr, err = read_provanddata({'directory': reference_dir}, entityid)
    assert entityid == calculate_data_hash(rawprov)
    # calculate_sign_hash performs some json magic which may affect the format. Therefore, compare
    # against the standardized json format which is used in the remaining code.
    assert calculate_data_hash(json.dumps(json.loads(rawprov), ensure_ascii=False,
                                          sort_keys=True).encode(model_encoding)) == calculate_sign_hash(rawprov)

    js = json.loads(rawprov)
    js['signature'] = {'person:familyName': 'Mustermensch', 'person:givenName': 'Maxi',
                       'provtool:signature': 'abcdef', 'provtool:timestampsignature': 'abcdef'}
    signprov = json.dumps(js, ensure_ascii=False, sort_keys=True)
    # calculate_sign_hash performs some json magic which may affect the format. Therefore, compare
    # against the standardized json format which is used in the remaining code.
    assert calculate_data_hash(json.dumps(json.loads(rawprov), ensure_ascii=False,
                                          sort_keys=True).encode(model_encoding)) == calculate_sign_hash(signprov.encode(model_encoding))

def test_convert_rawprov2containerprov(reference_dir):
    entityid = '29b2006eddfac9a26f4c5d98d63ba14c3096b2b461f9c8364b26c3670ab00c23'
    print(os.path.join(reference_dir, f'{entityid}.prov'))
    rawprov, dr, err = read_provanddata({'directory': reference_dir}, entityid)
    containerprov = convert_rawprov2containerprov(rawprov)
    rj = json.loads(rawprov)
    cj = json.loads(containerprov)

    assert 'self' in rj['entity']
    assert 'self' not in cj['entity']
    assert entityid in cj['entity']

def test_signatures(reference_dir):
    # In Windows, openssl may be supported by wsl but first tests indicate low performance. To be
    # supported only in the future.
    if not os.name == 'posix':
        assert false, f'Unrecognized operating system: {os.name}'

    if shutil.which('openssl') is None:
        assert false, 'No openssl found'

    entityid = '29b2006eddfac9a26f4c5d98d63ba14c3096b2b461f9c8364b26c3670ab00c23'
    rawprov, dr, err = read_provanddata({'directory': reference_dir}, entityid)
    timestampserver = 'http://zeitstempel.dfn.de'
    private_key_signer = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with requests_mock.Mocker() as m:
        m.post(timestampserver, content=b'timestampreply')

        prov_sig, signature, timestampsignature = sign(rawprov, 'Mustermensch', 'Maxi', private_key_signer, timestampserver)
        assert json.loads(prov_sig)['signature']['person:familyName'] == 'Mustermensch'
        assert json.loads(prov_sig)['signature']['person:givenName'] == 'Maxi'

        assert json.loads(prov_sig)['signature']['provtool:signature'] == calculate_data_hash(signature)
        assert json.loads(prov_sig)['signature']['provtool:timestampsignature'] == calculate_data_hash(timestampsignature)
        assert json.loads(prov_sig)['signature']['provtool:timestampsignature'] == calculate_data_hash(b'timestampreply')
