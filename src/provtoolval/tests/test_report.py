import os
import pytest
import tempfile

from distutils import dir_util
from pathlib import Path

from provtoolval.report import create_csv_report, create_html_report

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


def test_html_report(reference_dir):
    report_file = os.path.join(reference_dir, 'validation_report.html')
    create_html_report(check_result=[
        {'entity': '1234', 'data': 'abc123', 'name': 'Test1.txt', 'valid': True, 'used_by': ['5678', '9012'], 'activity': 'Test1', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
        {'entity': '5678', 'data': 'def567', 'name': 'Test2.txt', 'valid': True, 'used_by': None, 'activity': 'Test2', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
        {'entity': '5678', 'data': 'def567', 'name': 'Test2.txt', 'valid': True, 'used_by': {}, 'activity': 'Test3', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
    ], filename=report_file)

    assert os.path.exists(report_file)
    with open(os.path.join(reference_dir, 'report.html'), 'r') as reference, open(report_file, 'r') as report:
        assert reference.read() == report.read()


def test_csv_report(reference_dir):
    report_file = os.path.join(reference_dir, 'validation_report.csv')
    create_csv_report(check_result=[
        {'entity': '1234', 'data': 'abc123', 'name': 'Test1.txt', 'valid': True, 'used_by': ['5678', '9012'], 'activity': 'Test1', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
        {'entity': '5678', 'data': 'def567', 'name': 'Test2.txt', 'valid': True, 'used_by': None, 'activity': 'Test2', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
        {'entity': '5678', 'data': 'def567', 'name': 'Test2.txt', 'valid': True, 'used_by': {}, 'activity': 'Test3', 'start_time': '2020-11-18T20:19:00+01:00', 'end_time': '2020-11-18T20:20:00+01:00'},
    ], filename=report_file)

    assert os.path.exists(report_file)
    with open(os.path.join(reference_dir, 'report.csv'), 'r') as reference, open(report_file, 'r') as report:
        
        assert reference.read() == report.read()
