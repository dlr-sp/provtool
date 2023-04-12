import os
import pytest
import re
import tempfile

from distutils import dir_util
from pathlib import Path

from provtoolval.comparator import dircompare, filescompare

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


def test_dircompare_without_usage(reference_dir):
    dir1 = os.path.join(reference_dir, 'dir1')
    dir2 = os.path.join(reference_dir, 'dir2')

    def remove_comment(filename, byte_content):
        # This should be true for all test files. In general, other conditions should apply.
        assert filename.endswith('.txt')
        replaced = re.sub('^#.*\n', '', byte_content.decode('utf-8'))
        return replaced.encode('utf-8')

    compared = dircompare(dir1, dir2, remove_comment)
    matching = compared[compared['matching']]
    notmatching = compared[~compared['matching']]

    assert len(matching) == 5
    assert len(notmatching) == 7

    assert 'test1.txt' in matching['label_left'].values
    assert 'test2.txt' in matching['label_left'].values
    assert 'test7.txt' in matching['label_left'].values
    assert 'test8.txt' in matching['label_left'].values
    assert 'test9.txt' in matching['label_left'].values
    assert 'test3.txt' in notmatching['label_left'].values
    assert 'test3.txt' in notmatching['label_right'].values
    assert 'test4.txt' in notmatching['label_left'].values
    assert 'test5.txt' in notmatching['label_left'].values
    assert 'test5.txt' in notmatching['label_right'].values
    assert 'test6.txt' in notmatching['label_right'].values
    assert 'test6.txt' in notmatching['label_left'].values


def test_dircompare_with_usage(reference_dir):
    dir3 = os.path.join(reference_dir, 'dir3')
    dir4 = os.path.join(reference_dir, 'dir4')
    compared = dircompare(dir3, dir4, None)
    matching = compared[compared['matching']]
    notmatching = compared[~compared['matching']]

    assert len(matching) == 1
    assert len(notmatching) == 0


def test_filescompare(reference_dir):
    dir1 = os.path.join(reference_dir, 'dir1')
    dir2 = os.path.join(reference_dir, 'dir2')

    dir1_files = [os.path.join(dir1, f) for f in ['cf7b4562b819ad1941f715553a67881c4c328b82063775de2355c4be659e5da5.prov', '31f58430861efaa9d9417a5d2926793377f02a80b961d84be90558dc47c7be0f.prov']]
    dir2_files = [os.path.join(dir2, f) for f in ['9e4f6bb28e5ec03d54d6ed03ee0515b0ad1e0eafcf019e5f090ce1872df26321.prov', '3f31921e31d219a62d3f8b6193ab6984990907d8c66c0492cd607290dbc66af9.prov']]
    compared = filescompare(dir1_files, dir2_files)
    matching = compared[compared['matching']]
    notmatching = compared[~compared['matching']]

    assert len(matching) == 2
    assert len(notmatching) == 0

    assert 'test1.txt' in matching['label_left'].values
    assert 'test2.txt' in matching['label_left'].values
