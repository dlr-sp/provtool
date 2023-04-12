import argparse
import os
import textwrap
import sys

from cryptography.hazmat.primitives import serialization

from provtoolutils.constants import model_encoding
from provtoolutils.utilities import calculate_data_hash, sign

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


def main():
    usage_message = """
    %(prog)s [options]
    """
    parser = argparse.ArgumentParser('Provenance signatures', usage=usage_message,
                                     formatter_class=argparse.RawTextHelpFormatter
                                     )
    parser.add_argument('--provfile', help=textwrap.dedent(
        '''
            Path to provenance file to sign.
        '''
    ))
    parser.add_argument('--private', help=textwrap.dedent(
        '''
            Path to private key file.
        '''
    ))
    parser.add_argument('--familyname', help=textwrap.dedent(
        '''
            The family name of the signer.
        '''
    ))
    parser.add_argument('--givenname', help=textwrap.dedent(
        '''
            The given name of the signer.
        '''
    ))
    parser.add_argument('--timestampserver', help=textwrap.dedent(
        '''
            URL fo timestamp server, for example http://zeitstempel.dfn.de
        '''
    ))

    args = parser.parse_args()

    rawprov, dr, err = read_provanddata({'directory': os.path.dirname(args.provfile)},
                                        os.path.basename(args.provfile).replace('.prov', ''))
    with open(args.private, 'rb') as pk:
        private_key = serialization.load_pem_private_key(pk.read(), password=None)

        signprov, signature, tsignature = sign(rawprov, args.familyname, args.givenname,
                                               private_key, args.timestampserver)
        sph = calculate_data_hash(signprov.encode(model_encoding))
        base = os.path.dirname(args.provfile)
        with open(os.path.join(base, sph) + '.prov', 'wb') as sp:
            sp.write(signprov.encode(model_encoding))
        with open(os.path.join(base, calculate_data_hash(signature)), 'wb') as sp:
            sp.write(signature)
        with open(os.path.join(base, calculate_data_hash(tsignature)), 'wb') as sp:
            sp.write(tsignature)


if __name__ == '__main__':  # pragma: no cover
    main()
