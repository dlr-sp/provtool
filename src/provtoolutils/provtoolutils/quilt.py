from typing import List


class Row:
    """
    A row in a quilt matrix.

    A quilt matrix is a representation of a layered directed graph.

    A row corresponds to one node. It is assumed, that a node is uniquely identified by an id.

    The dependencies to the next layer (dep_to_next_layer) are given as a list with the length equal to the number of
    nodes in the next layer. The list contains 1 to indicate a dependency and 0 otherwise. The ids corresponding to the
    indices in this list are given in ids_for_dep.

    Dependencies to other levels than the next one are given as list of ids in additional_dep.
    """
    def __init__(self, length, id, layer, ids_for_dep):
        self.length = length
        self.dep_to_next_layer = [0 for _ in range(length)]
        self.additional_dep = []
        self.id = id
        self.ids_for_dep = ids_for_dep
        self.layer = layer


class Matrix:
    """
    A two-sided matrix. It shares the same y-axis (elements) but has a left and right side. There is a header for each
    side. There is no restriction on header or corresponding side in terms of a relation between them. Making such a
    relation is totally up to the application logic.
    """
    def __init__(self, left_header: List[str] = None, right_header: List[str] = None,
                 left: object = None, right: object = None, elements: List[str] = None):
        """
        :param left_header: A list of names for each entry on the left side.
        :param right_header: A list of names for each entry on the right side.
        :param left: The left side of Matrix. It is expected to be sparse. Indexing is done via [i, j].
        :param right: The right side of Matrix. It is expected to be sparse. Indexing is done via [i, j].
        :param elements: A list of names for each element.
        """
        self.left_header = [] if left_header is None else left_header
        self.right_header = [] if right_header is None else right_header
        self.left = {} if left is None else left
        self.right = {} if right is None else right
        self.elements = [] if elements is None else elements


class Quilt:
    """
    A quilt is combination of two sided matrices. See: Juhee Bae and Ben Watson: "Developing and Evaluating Quilts for
    the Depiction of Large Layered Graphs", IEEE TRANSACTIONS ON VISUALIZATION AND COMPUTER GRAPHICS (2011)
    """

    @staticmethod
    def _dictionarize(gen, key, many=False):
        result = {}
        for d in gen:
            if many:
                li = result.get(d[key], [])
                li.append(d)
            else:
                li = d
            result[d[key]] = li
        return result

    @staticmethod
    def make_quilt(data):
        """
        :param data: A list of dictionaries having the following attributes: id, level, depends_on with the following
        properties: id: unique int/string, level: int, depends_in: list of id's.
        :return: An ordered list of provtoolutils.quilt.Row's. The ordering is done by level.
        """
        data_at_levels = Quilt._dictionarize((d for d in data), 'level', True)
        data_at_ids = Quilt._dictionarize((d for d in data), 'id')
        levels = list(data_at_levels.keys())
        levels.sort()
        matrix = []

        for level in levels:
            for data_at_level in data_at_levels[level]:
                if level < levels[-1]:
                    row = Row(len(data_at_levels[level + 1]), data_at_level['id'], level,
                              [d['id'] for d in data_at_levels[level + 1]]
                              )
                    matrix.append(row)
                    for dep_id in data_at_level['depends_on']:
                        dep = data_at_ids[dep_id]
                        if dep['level'] == data_at_level['level'] + 1:
                            row.dep_to_next_layer[data_at_levels[level + 1].index(dep)] = 1
                        else:
                            row.additional_dep.append(dep_id)
                else:
                    row = Row(0, data_at_level['id'], level, [])
                    matrix.append(row)
                    for dep_id in data_at_level['depends_on']:
                        row.additional_dep.append(dep_id)

        return matrix
