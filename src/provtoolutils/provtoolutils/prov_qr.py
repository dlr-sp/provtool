import argparse
import math
import os
import shutil
import subprocess
import sys
import textwrap

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def read_provanddata(options, cid):
    discovered_plugins = entry_points(group='provtoolutils.reader')
    for dp in discovered_plugins:
        try:
            pr, dr, err = getattr(dp.load(), 'read_provanddata')(options, cid)
            return pr, dr, err
        # Catch any exception. These may come from arbitrary plugins and may be unpredictable. On
        # the other hand the integrity of a container (data and provenance) can always be checked.
        # Therefore, if any of the readers return without an error, it is sufficient.
        except Exception as e:
            print(e)

    return None, None, True


def qr(prov_file: str, image_file: str):
    assert os.path.exists(prov_file), f'No file named {prov_file}'
    assert shutil.which('jabcodeWriter') is not None, 'jabcodeWriter not in path'

    json_str, dr, err = read_provanddata({'directory': os.path.dirname(prov_file)},
                                         os.path.basename(prov_file).replace('.prov', ''))

    # See spec: Minimum of primary/secondary bit number, 8 colors, side version 32
    max_num_bits = 26925
    # It is a little bit unclear according to the spec, what will happen to non-ASCII characters.
    num_symbols = math.ceil(len(json_str)/(max_num_bits/8))

    symbol_pos = [str(i) for i in range(0, num_symbols)]
    symbol_ver = ['32 32' for i in range(0, num_symbols)]

    cmd = (f"jabcodeWriter --input '{json_str}' --output {image_file} --symbol-number {str(num_symbols)} " +
           f"--symbol-position {' '.join(symbol_pos)} --symbol-version {' '.join(symbol_ver)}")
    subprocess.run(cmd, shell=True)


def main():
    usage_message = """
    %(prog)s [options]


    Example:

    python -m provtoolutils.prov_qr --provfile /home/testuser/test/1e345.prov --imagefile /tmp/provqr.png
    """
    parser = argparse.ArgumentParser('Provenance QR code generator', usage=usage_message,
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--provfile', help=textwrap.dedent(
        '''
            The path to the provennace file, which should be analysed.
        '''
    ))
    parser.add_argument('--imagefile', help=textwrap.dedent(
        '''
            The path to the image file which should be created and will contain the QR code.
        '''
    ))

    args = parser.parse_args()

    qr(args.provfile, args.imagefile)


if __name__ == '__main__':  # pragma: no cover
    main()
