import argparse
import datetime
import dateutil.parser
import git
import os
import sqlite3
import textwrap

from git import Repo

from provtoolutils.model import make_provstring, Activity, Entity, Person
from provtoolutils.utilities import calculate_data_hash


class Standalone:

    def __init__(self, db='provtool.db'):
        self.conn = sqlite3.connect(db)

        self.bar = '##############################'

        columns = [
            'entity_path',
            'author_family_name', 'author_given_name',
            'activity_location', 'activity_label', 'activity_means', 'activity_time', 'entity_id'
        ]

        col_def_string = ', '.join(['{} varchar'.format(c) for c in columns])
        col_string = ', '.join(columns)
        val_string = ', '.join(['\'\'' for c in columns])
        self.conn.executescript('create table if not exists provtool({})'.format(col_def_string))
        self.conn.executescript('insert into provtool ({}) values ({})'.format(col_string, val_string))

    @staticmethod
    def yn_feedback(label):
        yn = ''
        while yn != 'n' and yn != 'y':
            yn = input(label)
        return yn

    def heading(self, text):
        print('\n\n' + self.bar)
        print(text)
        print(self.bar)

    def ask(self, key, question_label=None):
        rs = self.conn.execute('select {} from provtool'.format(key)).fetchone()[0]
        default = ''
        yn = ''
        if rs and len(rs) > 0:
            default = rs
            yn = self.yn_feedback('Keep the following entry for {}: {} [y/n]'.format(key, default))
        if yn == 'y':
            return default
        else:
            inp = input(question_label if question_label is not None else f'Please enter a value for {key}: \n').strip()
            self.conn.execute("update provtool set {} = ?".format(key), (inp,))
            self.conn.commit()
            return inp

    def write_prov_file(self, activity_time: datetime, activity_location, activity_label,
                        activity_means, used, entity_path, author):
        activity = Activity(start_time=activity_time, end_time=activity_time, location=activity_location,
                            label=activity_label, means=activity_means, used=used, generate_uuid=False)

        with open(entity_path, 'rb') as f:
            datab = f.read()
            rawprov = make_provstring(os.path.basename(entity_path), Entity.FILE, author, activity,
                                      calculate_data_hash(datab)
                                      )
            entityid = calculate_data_hash(rawprov)

            provfilename = '{}.prov'.format(entityid)
            rawfilename = calculate_data_hash(datab)

            provfile = os.path.join(os.path.dirname(entity_path), provfilename)
            rawfile = os.path.join(os.path.dirname(entity_path), rawfilename)
            print('Writing file: {}'.format(provfile))

            with open(provfile, 'wb') as target_f:
                target_f.write(rawprov)
            with open(rawfile, 'wb') as target_f:
                target_f.write(datab)
            with open(os.path.join(os.path.dirname(entity_path), 'provtool_filemapping.txt'), 'a') as mapping_file:
                mapping_file.write('{}={}'.format(entity_path, provfilename))

    def run(self):
        self.heading('File')
        entity_path = self.ask('entity_path')

        author = None
        last = author
        while True:
            self.heading('Author')
            author_family_name = self.ask('author_family_name')
            author_given_name = self.ask('author_given_name')

            author_ = Person(family_name=author_family_name, given_name=author_given_name)
            if author is None:
                author = author_
                last = author
            else:
                last.acted_on_behalf_of = author_
                last = author_

            yn = self.yn_feedback('Are there more authors? [y/n]')
            if yn == 'n':
                break

        self.heading('Activity')
        activity_location = self.ask('activity_location')
        activity_label = self.ask('activity_label')
        activity_means = self.ask('activity_means')
        activity_time = dateutil.parser.parse(self.ask('activity_time'))

        used = []
        if self.yn_feedback('Are there used entities? [y/n]') == 'y':
            while True:
                used.append(self.ask('entity_id'))

                yn = self.yn_feedback('Are there more used entities? [y/n]')
                if yn == 'n':
                    break

        self.write_prov_file(activity_time, activity_location, activity_label, activity_means, used,
                             entity_path, author
                             )

    def run_repo(self, repo_path, file_path, activity_description=''):
        repo = Repo(repo_path, search_parent_directories=True, odbt=git.GitCmdObjectDB)
        if repo.is_dirty():
            raise ValueError('Repository is dirty. Please commit before using this tool')
        commit = next(iter(repo.iter_commits(paths=file_path, max_count=1)))
        # The Linux timestamp should be in UTC ALWAYS. Use the explicit time zone for converting.
        dt = datetime.datetime.fromtimestamp(commit.committed_datetime.timestamp(), tz=datetime.timezone.utc)
        self.write_prov_file(dt, 'Unkown', f'Git commit {commit.hexsha}' +
                             (f'. {activity_description}' if len(activity_description) > 0 else ''),
                             '-', [], os.path.join(repo_path, file_path),
                             Person(commit.author.name.split(' ')[0], " ".join(commit.author.name.split(' ')[1:]))
                             )

        repo.git.clear_cache()
        repo.close()


if __name__ == '__main__':  # pragma: no cover
    usage_message = """
        %(prog)s [options]


        Example:

        python -m provtoolutils.standalone
        python -m provtoolutils.standalone --repopath <path to repository> --filepath <path to file within repository>
        """
    parser = argparse.ArgumentParser('Provenance standalone conversion', usage=usage_message,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--repopath', help=textwrap.dedent(
        '''
            Path to the repository, which should be used
        '''
    ))
    parser.add_argument('--filepath', help=textwrap.dedent(
        '''
            File within the repository, which should be used. The path should be relative to the repository root.
        '''
    ))

    args = parser.parse_args()

    if args.repopath or args.filepath:
        Standalone().run_repo(args.repopath, args.filepath)
    else:
        Standalone().run()
