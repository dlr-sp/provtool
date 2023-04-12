import datetime
import os
import pytest
import tempfile

from distutils import dir_util
from pathlib import Path

from matplotlib import pyplot as plt

from provtoolutils.constants import model_encoding
from provtoolutils.utilities import calculate_data_hash
from provtoolutils.model import make_provstring, ActingSoftware, Activity, Entity, Person
from provtoolvis import file2quilt


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


def setup_3_act(base_dir):
    ag1 = Person('Max', 'Mustermann')
    ag2 = ActingSoftware(ag1, 'Max Mustermann', '-', 'Software2', '-')
    act1 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity1',
                    '-',
                    []
                    )

    data = ''.encode(model_encoding)
    datahash = calculate_data_hash(data)

    rawprov1 = make_provstring('test1', Entity.FILE, ag2, act1, datahash)
    entityid1 = calculate_data_hash(rawprov1)
    file1 = os.path.join(base_dir, entityid1) + '.prov'
    with open(file1, 'wb') as f:
        f.write(rawprov1)

    ag3 = Person('Max', 'Mustermann2')
    ag4 = ActingSoftware(ag3, 'Max Mustermann', '-', 'Software4', '-')
    act2 = Activity(datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity2',
                    '-',
                    [entityid1, 'missing']
                    )

    rawprov2 = make_provstring('test2', Entity.FILE, ag4, act2, datahash)
    entityid2 = calculate_data_hash(rawprov2)
    file2 = os.path.join(base_dir, entityid2) + '.prov'
    with open(file2, 'wb') as f:
        f.write(rawprov2)

    rawprov3 = make_provstring('test3', Entity.FILE, ag4, act2, datahash)
    entityid3 = calculate_data_hash(rawprov3)
    file3 = os.path.join(base_dir, entityid3) + '.prov'
    with open(file3, 'wb') as f:
        f.write(rawprov3)

    return file1, file2, file3


def test_search_prov_files_for_relations(base_dir):
    f1, f2, f3 = setup_3_act(base_dir)

    ags, acts, used, gen, act2ag, act2ag_trans, id2label = \
        file2quilt.search_prov_files_for_relations({'directory': base_dir}, [os.path.basename(f1).replace('.prov', ''),
                                                                             os.path.basename(f2).replace('.prov', ''),
                                                                             os.path.basename(f3).replace('.prov', '')])

    # 4 ags expected + 'UNKNOWN' dummy agent.
    assert len(ags) == 5
    # 2 acts expected + 'UNKNOWN' dummy activity.
    assert len(acts) == 3
    assert len(used) == 1
    # 2 gen expected + dummy.
    assert len(gen) == 4
    # 2 mappings expected + dummy mapping.
    assert len(act2ag) == 3
    assert len(act2ag_trans) == 3
    # 9 labels expected + 3 dummy label
    assert len(id2label) == 12


def test_find_relevant_ids(base_dir):
    # Do not use the default test setup because here the last entity should be separated from the first two.

    ag1 = Person('Max', 'Mustermann')
    ag2 = ActingSoftware(ag1, 'Max Mustermann', '-', 'Software2', '-')
    act1 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity1',
                    '-',
                    []
                    )

    data = ''.encode(model_encoding)
    datahash = calculate_data_hash(data)
    with open(os.path.join(base_dir, datahash), 'wb') as f:
        f.write(data)

    rawprov1 = make_provstring('test1', Entity.FILE, ag2, act1, datahash)
    entityid1 = calculate_data_hash(rawprov1)
    file1 = os.path.join(base_dir, entityid1) + '.prov'
    with open(file1, 'wb') as f:
        f.write(rawprov1)

    ag3 = Person('Max', 'Mustermann2')
    ag4 = ActingSoftware(ag3, 'Max Mustermann', '-', 'Software4', '-')
    act2 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity2',
                    '-',
                    [entityid1]
                    )

    rawprov2 = make_provstring('test2', Entity.FILE, ag4, act2, datahash)
    entityid2 = calculate_data_hash(rawprov2)
    file2 = os.path.join(base_dir, entityid2) + '.prov'
    with open(file2, 'wb') as f:
        f.write(rawprov2)

    act3 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity3',
                    '-',
                    []
                    )

    rawprov3 = make_provstring('test3', Entity.FILE, ag4, act3, datahash)
    entityid3 = calculate_data_hash(rawprov3)
    file3 = os.path.join(base_dir, entityid3) + '.prov'
    with open(file3, 'wb') as f:
        f.write(rawprov3)

    _, _, used, generations, act2ag, _, _ = \
        file2quilt.search_prov_files_for_relations({'directory': base_dir}, [os.path.basename(file1).replace('.prov', ''),
                                                                             os.path.basename(file2).replace('.prov', ''),
                                                                             os.path.basename(file3).replace('.prov', '')])

    rel_ids = file2quilt.find_relevant_ids(entityid2, used, generations, act2ag)

    # There are: 2 Persons, 2 ActingSoftwares, 2 Activities and 2 Entities. Nevertheless, only the agents directly
    # responsible for the activity are taken into account and thus only 6 ids expected.
    assert len(rel_ids) == 6


def test_find_relevant_ids_with_missing(base_dir):
    # Do not use the default test setup because here the last entity should be separated from the first two.

    ag1 = Person('Max', 'Mustermann')
    ag2 = ActingSoftware(ag1, 'Max Mustermann', '-', 'Software2', '-')
    act1 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity1',
                    '-',
                    []
                    )

    data = ''.encode(model_encoding)
    datahash = calculate_data_hash(data)
    with open(os.path.join(base_dir, datahash), 'wb') as f:
        f.write(data)

    rawprov1 = make_provstring('test1', Entity.FILE, ag2, act1, datahash)
    entityid1 = calculate_data_hash(rawprov1)
    file1 = os.path.join(base_dir, entityid1) + '.prov'
    with open(file1, 'wb') as f:
        f.write(rawprov1)

    ag3 = Person('Max', 'Mustermann2')
    ag4 = ActingSoftware(ag3, 'Max Mustermann', '-', 'Software4', '-')
    act2 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity2',
                    '-',
                    [entityid1]
                    )

    rawprov2 = make_provstring('test2', Entity.FILE, ag4, act2, datahash)
    entityid2 = calculate_data_hash(rawprov2)
    file2 = os.path.join(base_dir, entityid2) + '.prov'
    with open(file2, 'wb') as f:
        f.write(rawprov2)

    act3 = Activity(
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    '-',
                    'Activity3',
                    '-',
                    [entityid2, 'missing']
                    )
    rawprov3 = make_provstring('test3', Entity.FILE, ag4, act3, datahash)
    entityid3 = calculate_data_hash(rawprov3)
    file3 = os.path.join(base_dir, entityid3) + '.prov'
    with open(file3, 'wb') as f:
        f.write(rawprov3)

    _, _, used, generations, act2ag, _, _ = \
        file2quilt.search_prov_files_for_relations({'directory': base_dir}, [os.path.basename(file1).replace('.prov', ''),
                                                                             os.path.basename(file2).replace('.prov', ''),
                                                                             os.path.basename(file3).replace('.prov', '')])
    rel_ids = file2quilt.find_relevant_ids(entityid3, used, generations, act2ag)
    # There are: 2 Persons, 2 ActingSoftwares, 2 Activities and 3 Entities. Nevertheless, only the agents directly
    # responsible for the activity are taken into account and thus only 6 ids expected.
    assert len(rel_ids) == 12


def test_find_relevant_usage_and_generation(base_dir):
    file1, file2, file3 = setup_3_act(base_dir)

    agents, activities, used, generations, act2ag, act2ag_trans, id2label = \
        file2quilt.search_prov_files_for_relations({'directory': base_dir}, [os.path.basename(file1).replace('.prov', ''),
                                                                             os.path.basename(file2).replace('.prov', ''),
                                                                             os.path.basename(file3).replace('.prov', '')])
    used_for_specified_entity = file2quilt.find_relevant_ids(
                                                             os.path.basename(file3).replace('.prov', ''),
                                                             used,
                                                             generations,
                                                             act2ag
                                                             )
    relevant_used, relevant_generations = file2quilt.find_relevant_usage_and_generation(
                                                                                        used_for_specified_entity,
                                                                                        used,
                                                                                        generations
                                                                                        )

    assert len(relevant_used) == 1
    # 2 expected + one dummy.
    assert len(relevant_generations) == 3


def test_create_matrices(base_dir):
    file1, file2, file3 = setup_3_act(base_dir)

    agents, activities, used, generations, act2ag, act2ag_trans, id2label = \
        file2quilt.search_prov_files_for_relations({'directory': base_dir}, [os.path.basename(file1).replace('.prov', ''),
                                                                             os.path.basename(file2).replace('.prov', ''),
                                                                             os.path.basename(file3).replace('.prov', '')])
    used_for_specified_entity = file2quilt.find_relevant_ids(
                                                             os.path.basename(file3).replace('.prov', ''),
                                                             used,
                                                             generations, act2ag
                                                             )
    relevant_used, relevant_generations = file2quilt.find_relevant_usage_and_generation(
                                                                                        used_for_specified_entity,
                                                                                        used,
                                                                                        generations
                                                                                        )

    matrices = file2quilt.create_matrices(
                                          activities,
                                          relevant_used,
                                          relevant_generations,
                                          used_for_specified_entity,
                                          id2label
                                          )

    assert len(matrices) == 2


def test_find_prov_ids_recursive(reference_dir):
    ids = file2quilt.find_prov_ids_recursive({'directory': reference_dir},
                                              '4854deb7749b6005cadd4eaa6622040b5b1e6c98b273309bd63db3deaf1ebbec')
    assert len(ids) == 2
    assert '28dbf4c384508cf78ca3d1245751bfb9b93a4eca377c0fa6214ec31e82157975' in ids
    assert '4854deb7749b6005cadd4eaa6622040b5b1e6c98b273309bd63db3deaf1ebbec' in ids


def test_main(reference_dir):
    image_file = os.path.join(reference_dir, 'test_out.png')
    file2quilt.main('4854deb7749b6005cadd4eaa6622040b5b1e6c98b273309bd63db3deaf1ebbec', image_file, {'directory': reference_dir})

    reference = plt.imread(os.path.join(reference_dir, 'test.png'))
    image = plt.imread(image_file)

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
