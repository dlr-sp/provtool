import matplotlib

from matplotlib import pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

from typing import Dict, List

from provtoolutils.quilt import Matrix


def _draw_entity_symbol(matrices, colors, numbers, symbol_size, space):
    offset_x, offset_y = 0, 0

    for mat in matrices:
        index_i = [k[0] for k in mat.left.keys()]
        for i, lh in enumerate(mat.left_header):
            rect = plt.Rectangle((offset_x + (symbol_size + space) * i, offset_y), symbol_size,
                                 symbol_size, fc=colors[lh])
            plt.gca().add_patch(rect)

            _draw_entity_index(str(numbers[lh]), offset_x + (symbol_size + space) * i, offset_y,
                               text_size=symbol_size / 2, bb_width=symbol_size,
                               bb_height=symbol_size)
        offset_x = offset_x + max(index_i, default=0) * (symbol_size + space) + 2 * (symbol_size + space)
        offset_y = offset_y - symbol_size - space - len(mat.elements) * (symbol_size + space)


def _draw_generated_symbol(matrices, symbol_size, space):
    offset_x, offset_y = 0, 0
    for mat in matrices:
        index_i = [k[0] for k in mat.left.keys()]
        index_j = [k[1] for k in mat.left.keys()]
        offset_y = offset_y - symbol_size - space
        for i in index_i:
            for j in index_j:
                if (i, j) in mat.left:
                    rect = plt.Rectangle((offset_x + (symbol_size + space) * i,
                                         offset_y - (symbol_size + space) * j), symbol_size,
                                         symbol_size, fc='#000000')
                    plt.gca().add_patch(rect)
        offset_x = offset_x + max(index_i, default=0) * (symbol_size + space) + 2 * (symbol_size + space)
        offset_y = offset_y - len(mat.elements) * (symbol_size + space)


def _draw_activity_symbol(matrices, symbol_size, space):
    offset_x, offset_y = 0, 0
    for mat in matrices:
        index_i = [k[0] for k in mat.left.keys()]
        offset_y = offset_y - symbol_size - space
        offset_x = offset_x + max(index_i, default=0) * (symbol_size + space) + symbol_size + space

        for i, _ in enumerate(mat.elements):
            rect = plt.Rectangle((offset_x, offset_y - (symbol_size + space) * i), symbol_size,
                                 symbol_size, fc='#c0c0c0')
            plt.gca().add_patch(rect)
        offset_x = offset_x + symbol_size + space
        offset_y = offset_y - len(mat.elements) * (symbol_size + space)


def _draw_used_symbol(matrices, colors, numbers, symbol_size, space):
    offset_x, offset_y = 0, 0
    for mat in matrices:
        index_i = [k[0] for k in mat.left.keys()]
        offset_x = offset_x + max(index_i, default=0) * (symbol_size + space) + 2 * (symbol_size + space)
        offset_y = offset_y - symbol_size - space

        index_i = [k[0] for k in mat.right.keys()]
        index_j = [k[1] for k in mat.right.keys()]
        for i in index_i:
            for j in index_j:
                if (i, j) in mat.right:
                    # Default dependency
                    if i < len(mat.right_header):
                        rect = plt.Rectangle((offset_x + (symbol_size + space) * i,
                                             offset_y - (symbol_size + space) * j), symbol_size, symbol_size,
                                             fc='#000000')
                        plt.gca().add_patch(rect)
                    # Special dependency.
                    else:
                        rect = plt.Rectangle((offset_x + (symbol_size + space) * i,
                                             offset_y - (symbol_size + space) * j), symbol_size, symbol_size,
                                             fc=colors[mat.right[i, j]], ec='#000000')
                        plt.gca().add_patch(rect)

                        _draw_entity_index(str(numbers[mat.right[i, j]]), offset_x + (symbol_size + space) * i,
                                           offset_y - (symbol_size + space) * j,
                                           text_size=symbol_size / 2, bb_width=symbol_size, bb_height=symbol_size)
        offset_y = offset_y - len(mat.elements) * (symbol_size + space)


def _draw_entity_index(text, x, y, text_size, bb_width, bb_height):
    text_path = TextPath((0, 0), text, size=text_size)
    extents = text_path.get_extents()
    text_path = text_path.transformed(Affine2D().translate(x + max(0, (bb_width - extents.width) / 2),
                                                           y + max(0, bb_height - extents.height) / 2))
    text_patch = PathPatch(text_path, edgecolor='w', facecolor='w', linewidth=0.1)
    plt.gca().add_patch(text_patch)

    return extents


def _draw_label(text, x, y, text_size, bb_height, rotate=False):
    text_path = TextPath((0, 0), text, size=text_size)
    extents = text_path.get_extents()
    text_path = text_path.transformed(Affine2D().rotate_deg(-90 if rotate else 0) + Affine2D().translate(
        x + max(0, (bb_height - extents.height) / 2), y))
    text_patch = PathPatch(text_path, edgecolor=None, facecolor='k', linewidth=0.1)
    plt.gca().add_patch(text_patch)

    return extents


def _draw_activity_label(matrices, x, size, space):
    offset_y = 0 - size - space
    max_element_text_extent = 0
    for mat in matrices:
        for j, elem in enumerate(mat.elements):
            extents = _draw_label(elem, x, offset_y - j * (size + space), text_size=size, bb_height=size)

            max_element_text_extent = max(max_element_text_extent, extents.width)
        offset_y = offset_y - (size + space)
        offset_y = offset_y - len(mat.elements) * (size + space)

    return max_element_text_extent


def _draw_entity_label(matrices, y, size, space):
    offset_x = 0
    for i, mat in enumerate(matrices):
        for j, lh in enumerate(mat.left_header):
            _draw_label(lh, offset_x + j * (size + space), y - space, text_size=size, bb_height=size, rotate=True)
        offset_x = offset_x + size + space
        offset_x = offset_x + len(mat.left_header) * (size + space)


def _draw_agent_label(agents, x, y, size, space):
    for i, ag in enumerate(agents):
        _draw_label(ag, x + i * (size + space), y, text_size=size, bb_height=size, rotate=True)


def _draw_association_symbol(matrices, agents, activity2agent, x, symbol_size, space):
    offset_y = 0 - symbol_size - space
    for i, mat in enumerate(matrices):
        for j, elem in enumerate(mat.elements):
            for k, _ag in enumerate(agents):
                if activity2agent[elem] == _ag:
                    rect = plt.Rectangle((x + k * (symbol_size + space),
                                         offset_y - j * (symbol_size + space)), symbol_size, symbol_size,
                                         fc='#000000')
                    plt.gca().add_patch(rect)
        offset_y = offset_y - (symbol_size + space)
        offset_y = offset_y - len(mat.elements) * (symbol_size + space)


def _create_entity_maps(matrices):
    cm = plt.get_cmap('plasma')
    colors = {}
    numbers = {}
    num_all_left_headers = sum([len(m.left_header) for m in matrices])
    left_header = 0

    for mat in matrices:
        for lh in mat.left_header:
            colors[lh] = cm(left_header / num_all_left_headers)
            numbers[lh] = left_header
            left_header = left_header + 1

    return colors, numbers


def _get_lower_right_quilt_corner(matrices, size, space):
    offset_x = 0
    for mat in matrices:
        index_i = [k[0] for k in mat.left.keys()]
        offset_x = offset_x + max(index_i, default=0) * (size + space) + 2 * (size + space)

    offset_y = 0 - size - space
    for mat in matrices:
        offset_y = offset_y - (size + space)
        offset_y = offset_y - len(mat.elements) * (size + space)

    return offset_x, offset_y


def create_image(matrices: List[Matrix], agents: List[str], activity2agent: Dict[str, str],
                 output_filename: str, matplotlibrc: str = None):
    """
    Create a quilt matrix image.
    :param matrices: A list of Matrix objects.
    :param agents: A list of agent names.
    :param activity2agent: A dictionary of activities to agents.
    :param output_filename: The (absolute) path to the image file which should be created.
    :param matplotlibrc: An optional file to set matplotlib plot preferences.
    """

    def _create_image():
        size = 10
        space = 5

        colors, numbers = _create_entity_maps(matrices)

        _draw_entity_symbol(matrices, colors, numbers, size, space)
        _draw_generated_symbol(matrices, size, space)
        _draw_activity_symbol(matrices, size, space)
        _draw_used_symbol(matrices, colors, numbers, size, space)

        offset_x, offset_y = _get_lower_right_quilt_corner(matrices, size, space)

        max_element_text_extent = _draw_activity_label(matrices, offset_x + space, size, space)

        agent_offset_x = offset_x + space + max_element_text_extent + space

        _draw_association_symbol(matrices, sorted(agents), activity2agent, agent_offset_x, size, space)
        _draw_agent_label(sorted(agents), agent_offset_x, offset_y, size, space)
        _draw_entity_label(matrices, offset_y, size, space)

        plt.axis('image')
        plt.axis('off')
        plt.savefig(output_filename, bbox_inches=None, dpi=600)

        plt.close()

    if matplotlibrc is not None:
        with matplotlib.rc_context(fname=matplotlibrc):
            _create_image()
    else:
        _create_image()
