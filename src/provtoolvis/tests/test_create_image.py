import hashlib
import os
import pytest
import tempfile

from matplotlib import pyplot as plt
from distutils import dir_util
from pathlib import Path

from provtoolutils.quilt import Matrix
from provtoolvis import create_image

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


def test_image_creation(base_dir):
    ml = {}
    ml[0, 0] = 'a'
    ml[1, 0] = 'b'
    mr = {}
    mr[0, 0] = 'c'
    mr[1, 0] = 'd'
    mr[2, 0] = 'x'
    m1 = Matrix(left_header=['a', 'b'], right_header=['c', 'd'], left=ml, right=mr, elements=['Akt1'])

    ml = {}
    ml[0, 0] = 'c'
    ml[1, 1] = 'd'
    mr = {}
    mr[0, 0] = 'x'
    mr[0, 1] = 'x'
    m2 = Matrix(left_header=['c', 'd'], right_header=['x'], left=ml, right=mr, elements=['Akt2', 'Akt3'])

    ml = {}
    ml[0, 0] = 'x'
    mr = {}
    m3 = Matrix(left_header=['x'], right_header=[], left=ml, right=mr, elements=['Akt4'])
    matrices = [m1, m2, m3]
    agents = ['Ag1', 'Ag2']
    activity2agents = {'Akt1': 'Ag1', 'Akt2': 'Ag2', 'Akt3': 'Ag2', 'Akt4': 'Ag1'}

    output_filename = os.path.join(base_dir, 'test.png')
    create_image.create_image(matrices, agents, activity2agents, output_filename, matplotlibrc='tests/matplotlibrc')

    assert os.path.exists(output_filename)
    image = plt.imread(output_filename)
    assert len(image) > 0
    assert len(image[0]) > 0


def test_image_content(base_dir, reference_dir):
    ml = {}
    ml[0, 0] = 'a'
    ml[1, 0] = 'b'
    mr = {}
    mr[0, 0] = 'c'
    mr[1, 0] = 'd'
    mr[2, 0] = 'x'
    m1 = Matrix(left_header=['a', 'b'], right_header=['c', 'd'], left=ml, right=mr, elements=['Akt1'])

    ml = {}
    ml[0, 0] = 'c'
    ml[1, 1] = 'd'
    mr = {}
    mr[0, 0] = 'x'
    mr[0, 1] = 'x'
    mr[0, 2] = 'x'
    m2 = Matrix(left_header=['c', 'd'], right_header=['x'], left=ml, right=mr, elements=['Akt2', 'Akt3', 'Akt5'])

    ml = {}
    ml[0, 0] = 'x'
    mr = {}
    m3 = Matrix(left_header=['x'], right_header=[], left=ml, right=mr, elements=['Akt4'])
    matrices = [m1, m2, m3]
    agents = ['Ag1', 'Ag2', 'Ag0']
    activity2agents = {'Akt1': 'Ag1', 'Akt2': 'Ag2', 'Akt3': 'Ag2', 'Akt4': 'Ag1', 'Akt5': 'Ag0'}

    output_filename = os.path.join(base_dir, 'test.png')
    create_image.create_image(matrices, agents, activity2agents, output_filename, matplotlibrc='tests/matplotlibrc')

    reference = plt.imread(os.path.join(reference_dir, 'test_create_image.png'))

    image = plt.imread(output_filename)

#    with open(os.path.join(reference_dir, 'test_create_image.png'), 'rb') as ref, open(output_filename, 'rb') as tar:
#        digest = hashlib.sha256()
#        digest.update(ref.read())
#        ref_hash = digest.hexdigest()
#
#        digest = hashlib.sha256()
#        digest.update(tar.read())
#        tar_hash = digest.hexdigest()
#        
#        assert ref_hash == tar_hash

    # There would be a much faster way to compare the images by just reading the images files as 
    # byte array and calculate and compare the hash. Unfortunately, this is not working because
    # Matplotlib saves metadata (for example the matplotlib-Version) within the image. This may 
    # change although the image data are the same.
    # Workarounds would be removing or overwritting the metadata. This would add complexity
    # without beeing useful for the provtoolutils functionality. => Skipped.
    assert len(reference) > 0
    assert len(reference[0]) > 0
    assert len(image) > 0
    assert len(image[0]) > 0
    assert len(reference) == len(image)
    assert len(reference[0]) == len(image[0])

    for index_i, i in enumerate(reference):
        for index_j, j in enumerate(i):
            # Iterate over all color channels
            for k in range(len(j)):
                assert reference[index_i][index_j][k] == image[index_i][index_j][k], 'Images differ at: {}, {}'.format(index_i, index_j)
