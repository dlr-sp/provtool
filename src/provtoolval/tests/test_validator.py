import jsonschema
import os
import pytest
import random
import tempfile

from distutils import dir_util
from pathlib import Path

from provtoolutils.utilities import calculate_data_hash
from provtoolval.constants import report_schema
from provtoolval.validator import Validator


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

def test_check(reference_dir):
    v = Validator(filelocation=reference_dir)

    # test2.txt
    check_result = v.check('f50a36489bb2efd260872f8c97b7382a4e9f92832256c16ecd2c4ef53e876551')
    jsonschema.validate(check_result, report_schema)
    assert len(check_result) == 2
    assert check_result[0]['valid']
    assert check_result[1]['valid']
    assert check_result[0]['used_by'] == ['f50a36489bb2efd260872f8c97b7382a4e9f92832256c16ecd2c4ef53e876551']
    assert len(check_result[1]['used_by']) == 0
    assert check_result[1]['used'] == ['e9021e24fde04440f829c18e337cb5b91c64ce49f0efc0c01d08bbe0babff438']

    # test3.txt
    check_result_2 = v.check('93eea484b4e263713cd0215720648eaedc557ed83101b29800c86e6217b3b079')
    jsonschema.validate(check_result_2, report_schema)
    assert len(check_result_2) == 2
    assert not check_result_2[0]['valid']
    assert not check_result_2[1]['valid']
    assert check_result_2[0]['used_by'] == ['93eea484b4e263713cd0215720648eaedc557ed83101b29800c86e6217b3b079']
    assert len(check_result_2[1]['used_by']) == 0

    # test4.txt
    check_result_3 = v.check('eacd6ad0653b95ab22df1c539442dcbaaf9c60f2155517c4203da01e746e0f45')
    jsonschema.validate(check_result_3, report_schema)
    assert len(check_result_3) == 3
    assert len(check_result_3[0]['used_by']) == 2
    assert len(check_result_3[1]['used_by']) == 1
    assert check_result_3[2]['used'] == [
                                         'e9021e24fde04440f829c18e337cb5b91c64ce49f0efc0c01d08bbe0babff438',
                                         'f50a36489bb2efd260872f8c97b7382a4e9f92832256c16ecd2c4ef53e876551'
                                        ]

    # Random, missing id
    random_bytes = bytearray((random.getrandbits(8) for i in range(100)))
    random_bytes_id = calculate_data_hash(random_bytes)
    check_result_random = v.check(random_bytes_id)
    jsonschema.validate(check_result_random, report_schema)
    assert not check_result_random[0]['valid']
