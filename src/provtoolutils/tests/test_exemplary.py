import datetime
import pytest
import tempfile

from provtoolutils.constants import model_encoding
from provtoolutils.utilities import calculate_data_hash
from provtoolutils.model import make_provstring, ActingSoftware, Activity, Entity, Person

@pytest.fixture
def base_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d

def test_example(base_dir):
    with open('tests/test_exemplary.py', 'r', encoding='utf-8') as f:

        # The data is generated between two points in time.
        start = datetime.datetime.now(datetime.timezone.utc)
        # Generate the data. Here, the script file content is used as an example.
        # The data needs to be a bytes.
        data = f.read().encode('utf-8')
        end = datetime.datetime.now(datetime.timezone.utc)

        # You can specify the location where the activity was done here. This
        # could be the hostname, ...
        activity_location = ''
        # The label is a short description of the activity.
        activity_label = 'Test activity'
        # Means is a longer explanation which gives a reason for generating the
        # data with this activity.
        activity_means = 'Creates a new file to showcase the usage of provenance \
            information together with files'

        # Someone is responsible for starting the process.
        responsible_given_name = 'Max'
        responsible_family_name = 'Mustermann'

        # The software which was used in the process needs to be specified.
        software_creator = 'Max Mustermann'
        software_version = '0.0.1'
        software_label = 'simple.py'
        # Where the software can be downloaded or enough information about the
        # software is stored.
        software_location = 'https://www.example.com'

        # Finally, the data needs a name to refer to.
        entity_name = 'Script file for demonstration purposes'

        activity = Activity(
            start,
            end,
            activity_location,
            activity_label,
            activity_means
        )
        responsible = Person(
            given_name=responsible_given_name,
            family_name=responsible_family_name
        )
        script = ActingSoftware(
            acted_on_behalf_of=responsible,
            creator=software_creator,
            version=software_version,
            label=software_label,
            location=software_location
        )

        rawprov = make_provstring(entity_name, Entity.FILE, script, activity, calculate_data_hash(data))
        entityid = calculate_data_hash(rawprov)

        # Optional: Write the file to disk. This is useful if the file is larger
        # and should be used directly. The upload could then be performed
        # asynchronously.
        with open('{}/{}.prov'.format(base_dir, entityid), 'wb') as out_file:
            out_file.write(rawprov)
        with open('{}/{}'.format(base_dir, calculate_data_hash(data)), 'wb') as out_file:
            out_file.write(data)
