import hashlib
import json
import logging
import requests
import subprocess
import tempfile

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from provtoolutils.constants import model_encoding


def calculate_data_hash(data):
    digest = hashlib.sha256()
    digest.update(data)
    datahash = digest.hexdigest()

    return datahash


def calculate_sign_hash(data):
    js = json.loads(data.decode(model_encoding))
    if 'signature' in js:
        del js['signature']

    return calculate_data_hash(json.dumps(js, ensure_ascii=False, sort_keys=True).encode(model_encoding))


def convert_rawprov2containerprov(raw_provstring):
    prov_obj = json.loads(raw_provstring)
    if 'self' not in prov_obj['entity']:
        raise ValueError('Expecting an entity with placeholder "self"')
    ent = prov_obj['entity']['self']
    if 'provtool:datahash' not in ent:
        raise ValueError('provtool:datahash attribute not found in provenance but it is required')
    ent_id = calculate_data_hash(raw_provstring)

    del prov_obj['entity']['self']
    prov_obj['entity'][ent_id] = ent

    return json.dumps(prov_obj, ensure_ascii=False, sort_keys=True)


def sign(rawprov: str, signer_familyname: str, signer_givenname: str, private_key_signer, timestampserver: str):
    logger = logging.getLogger('provtool')

    js = json.loads(rawprov)
    js['signature'] = {'person:familyName': signer_familyname, 'person:givenName': signer_givenname}

    signature = private_key_signer.sign(rawprov, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                             salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    js['signature']['provtool:signature'] = calculate_data_hash(signature)

    f_req = tempfile.NamedTemporaryFile()
    openssl = subprocess.run(['openssl', 'ts', '-query', '-cert', '-sha256', '-digest',
                              calculate_data_hash(rawprov), '-out', f_req.name])
    if openssl.returncode != 0:
        logger.error(f'Openssl call failed with the following arguments: {openssl.args}')

    with open(f_req.name, 'rb') as f:
        headers = {'Content-Type': 'application/timestamp-query'}
        r = requests.post(timestampserver, data=f.read(), headers=headers)
        timestampsignature = r.content
        js['signature']['provtool:timestampsignature'] = calculate_data_hash(timestampsignature)

        return json.dumps(js, ensure_ascii=False, sort_keys=True), signature, timestampsignature

    return None, None, None
