import argparse
import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def search(options, label):
    discovered_plugins = entry_points(group='provtoolutils.reader')
    paths = []
    for dp in discovered_plugins:
        try:
            found = getattr(dp.load(), 'search')(options, label)
            paths = paths + found
        # Catch any exception. These may come from arbitrary plugins and may be unpredictable. On
        # the other hand the integrity of a container (data and provenance) can always be checked.
        # Therefore, if any of the readers return without an error, it is sufficient.
        except Exception as e:
            print(e)

    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search prov files by entity name')
    parser.add_argument(
        '--entityname',
        type=str,
        help='The entity name.',
        required=True
    )
    group = parser.add_argument_group('prov')
    parser.add_argument(
        '--searchdir',
        type=str,
        help='The directory to be searched. The directory is searched recursively.',
    )
    args = parser.parse_args()
    if args.searchdir is None and args.searchfile is None:
        parser.error("at least one of --searchdir or --searchfile required")

    if args.searchdir is not None:
        paths = search({'directory': args.searchdir}, args.entityname)
        for p in paths:
            print(p)
