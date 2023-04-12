import argparse
import logging
import os
import sys
import textwrap

from provtoolval.report import create_csv_report, create_html_report
from provtoolval.validator import Validator


if __name__ == '__main__':
    logger = logging.getLogger('Validator')
    fh = logging.FileHandler('Validator.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)
    logger.setLevel(logging.WARNING)

    usage_message = """
        %(prog)s [options]


        Example:

        python -m provtoolval.main --filelocation directory --target a24fe... \
                --reportfile /home/test/.../report.html
        """
    parser = argparse.ArgumentParser('Provenance chain validator', usage=usage_message,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--filelocation', help=textwrap.dedent(
        '''
            The directory, which contains provenance container in file format.
        '''
    ), required=False)

    parser.add_argument('--target', help=textwrap.dedent(
        '''
            The hash of the file, for which the provenance chain should be validated.
        '''
    ), required=True)

    parser.add_argument('--reportfile', help=textwrap.dedent(
        '''
            The file, to which the validation report should be written.
        '''
    ), required=True)

    args = parser.parse_args()

    if not (args.reportfile.endswith('.html') or args.reportfile.endswith('.csv')):
        print('Invalid reportfile. Please specify a file ending with .html or .csv', file=sys.stderr)
        sys.exit(2)

    validator = Validator(args.filelocation)

    validation_result = validator.check(args.target)
    {
        '.html': create_html_report,
        '.csv': create_csv_report
    }.get(os.path.splitext(args.reportfile)[1], lambda x, y: None)(validation_result, args.reportfile)
