import json

from pytest import fixture
from provtoolutils.quilt import Quilt

@fixture
def quilt():
    # Data is in the following matrix form
    #
    #    0 1 2 3 4 5 6 7 8
    # 0    x       x   x
    # 1      x x
    # 2
    # 3          x
    # 4            x
    # 5              x   x
    # 6                x
    # 7                  x
    # 8
    data = [
        {'id': 8, 'level': 6, 'depends_on': []},
        {'id': 7, 'level': 6, 'depends_on': [8]},
        {'id': 6, 'level': 5, 'depends_on': [7]},
        {'id': 5, 'level': 4, 'depends_on': [8, 6]},
        {'id': 4, 'level': 3, 'depends_on': [5]},
        {'id': 3, 'level': 2, 'depends_on': [4]},
        {'id': 2, 'level': 1, 'depends_on': []},
        {'id': 1, 'level': 1, 'depends_on': [2, 3]},
        {'id': 0, 'level': 0, 'depends_on': [1, 7, 5]}
    ]

    return Quilt.make_quilt(data)

def test_make_quilt(quilt):
    # It is tested against the following quilt:
    #
    # 0  x   5 6
    #    1 2
    #    x   3  x
    #    2      4
    #           x  5  x 8
    #                 6
    #                 x  7 8
    #                    8

    assert quilt is not None
    assert len(quilt) == 9
    assert len(quilt[0].dep_to_next_layer) == 2
    assert len(quilt[0].additional_dep) == 2
    assert quilt[0].id == 0
    assert quilt[0].layer == 0
    assert quilt[0].ids_for_dep == [2, 1]
    assert quilt[0].additional_dep == [7, 5]
    assert len(quilt[1].dep_to_next_layer) == 1
    assert len(quilt[1].additional_dep) == 0
    assert quilt[1].id == 2
    assert quilt[1].layer == 1
    assert quilt[1].ids_for_dep == [3]
    assert len(quilt[2].dep_to_next_layer) == 1
    assert len(quilt[2].additional_dep) == 1
    assert quilt[2].id == 1
    assert quilt[2].layer == 1
    assert quilt[2].ids_for_dep == [3]
    assert quilt[2].additional_dep == [2]
    assert len(quilt[3].dep_to_next_layer) == 1
    assert len(quilt[3].additional_dep) == 0
    assert quilt[3].id == 3
    assert quilt[3].layer == 2
    assert quilt[3].ids_for_dep == [4]
    assert len(quilt[4].dep_to_next_layer) == 1
    assert len(quilt[4].additional_dep) == 0
    assert quilt[4].id == 4
    assert quilt[4].layer == 3
    assert quilt[4].ids_for_dep == [5]
    assert len(quilt[5].dep_to_next_layer) == 1
    assert len(quilt[5].additional_dep) == 1
    assert quilt[5].additional_dep == [8]
    assert quilt[5].id == 5
    assert quilt[5].layer == 4
    assert quilt[5].ids_for_dep == [6]
    assert len(quilt[6].dep_to_next_layer) == 2
    assert len(quilt[6].additional_dep) == 0
    assert quilt[6].id == 6
    assert quilt[6].layer == 5
    assert quilt[6].ids_for_dep == [8, 7]
    assert len(quilt[7].dep_to_next_layer) == 0
    assert len(quilt[7].additional_dep) == 0
    assert quilt[7].id == 8
    assert quilt[7].layer == 6
    assert len(quilt[8].dep_to_next_layer) == 0
    assert len(quilt[8].additional_dep) == 1
    assert quilt[8].id == 7
    assert quilt[8].layer == 6
    assert quilt[8].additional_dep == [8]
