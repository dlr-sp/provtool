# Provtoolutils

[[_TOC_]]

This python package contains a model and some utility methods for working with _provenance container_.

It can be used as a python library, as a wrapper around non provenance aware applications or as standalone application to add provenance information to non provenance aware files.

## Requirements

- Python 3.7+

## Installation & upgrade

Create a virtualenv for your project. Make sure, git is installed on your machine and you have a valid account for the repository.

Go to the repository [tags](https://github.com/dlr-sp/provtool/-/tags) and lookup the latest provtoolutils tag.

Activate your virtual environment and install via (replace {username} with your repository user and {tag} with the tag name you want to install):

```
pip install --upgrade "git+https://{username}@github.com/dlr-sp/provtool.git@{tag}#egg=provtoolutils&subdirectory=src/provtoolutils"
```

**Example**:

```
pip install --upgrade "git+https://max_mu@github.com/dlr-sp/provtool.git@provtoolutils_0.16.4#egg=provtoolutils&subdirectory=src/provtoolutils"
```

To verify a correct installation, type

```
pip show provtoolutils
```

## Building from source

Checkout the project and run:

```bash
cd provtool/src/utils
pip install -e .
```

## Test

Checkout the project and run:

```bash
cd provtool/src/provtoolutils
tox
```

Many of the tests use a test directory containing reference data. The approach for using the reference data is similar to https://stackoverflow.com/a/29631801.

## Usage

**Note**: The usage of the python library needs a _provenance container_ locator. Please install either [locator for container files](../provtoolutils_localcontainerreader)(preferred) or another suitable plugin.

### A wrapper around non provenance aware applications: Processing input/output directories

Assuming a simple [input-process-output behaviour](https://en.wikipedia.org/wiki/IPO_model) for tools, it is enough to connect each tool artefact with the corresponding inputs and some additional meta information to get a full provenance data set. The wrapper functionality supports this use case. It is assumed, that all information provided are accurate. Resilience against intentional attacks during data and provenance generation are out of the scope of this library.

The information needed for provenance are twofold: Static information about the
used tool, the reason why the tool is used, the person starting it, etc. On the
other hand, there are dynamic information like start/end times and responsible
user. The dynamic provenance information is given via parameter and agentinfo 
file while the static information must be provided by the user in a config.json 
file (see provtoolutils.constants.py for the corresponding schema definition):

```
{
   "agent": {
       "type": "software",
       "creator": "The author of the software",
       "version": "The software version. This can also be a git commit, ...",
       "label": "The software name",
       "location": "The location, where more information about the software is available",
       "acted_on_behalf_of": {
           "given_name": "The persons given name",
           "family_name": "The persons family name",
           "type": "person"
       }
   },
   "activity": {
       "location": "Name of the machine, where the activity was performed on",
       "label": "A short description/name of the activity",
       "means": "A long description and explanation, why the activity was performed"
   }
}
```

The corresponding agentinfo.json file looks like (see provtoolutils.constants.py for the corresponding schema definition):

```
  {
     "agent": {
         "given_name": "Frank",
         "family_name": "Dressel",
         "type": "person",
         "acted_on_behalf_of": {
             "label": "DLR",
             "type": "organization"
         }
     }
  }
```

Currently, the agentinfo file allows two types of elements: Organization and 
Person. The file is read from top to bottom; if there is an Organization, it 
must be the first entry.

Each element is started by a header [Organization] or [Person] and the necessary
attributes listed in the example file above.

The wrapper extracts information from _provenance container_ and creates new _provenance container_ based on static information from the config.json and agentinfo.json (see above), given parameters like start and end time and the content of input/output directory of the tool (under the assumptions, that all provenance files in input folder are r🐘).

The wrapper assumes a directory layout with an optional input directory containing _provenance container_ files and a mandatory output directory (may be empty), which
contains the result files of the process. Further information about the process despite the ones in the config.json and agent.json files are not needed.

<table><tr><td>
<b>Example</b>

Extract data from _provenance container_ input directory.

```bash
python -m provtoolutils.directorywrapper --inputdir input
```

</td></tr></table>

<table><tr><td>
<b>Example</b>

Convert data from output folder to _provenance container_.

```bash
python -m provtoolutils.directorywrapper --configfile config.json \
    --agentinfo agent.json --inputdir input --outputdir output \
    --start 2019-12-30T23:55:00+00:00 --end 2019-12-31T15:16:17+00:00
```

There is an additional optional argument --noraw, which skips renaming the original data file.

</td></tr></table>

Tools may be started from a higher level workflow. In such a case, the information that the workflow was responsible for starting the tool may be interesting.
Unfortunately, the workflow may still be running while the output of a single tool needs to be processed with provenance information. In such a case, an
artificial activity id can be generated with the option _--createactivityid_, which will print out a single id which can be assigned to a variable for further
usage.  The artificially created activity id can be used later on for establishing the relation between workflow and tools and finally to create the workflow
provenance. The full process looks like the following.

<table><tr><td>
<b>Create artificial activity id</b>

```bash
ACTIVITY=$(python -m provtoolutils.directorywrapper --createactivityid)
```

</td></tr>
<tr><td>
<b>First tool</b>

```bash
<command for first tool>
python -m provtoolutils.directorywrapper --configfile config.json \
    --agentinfo agent.json --inputdir <toolinput> --outputdir <tooloutput> \
    --start 2019-12-30T23:55:00+00:00 --end 2019-12-31T15:16:17+00:00 \
    --startedby $ACTIVITY
```

</td></tr>
<tr><td>
<b>Further tools</b>

```bash
...
...
```

</td></tr>
<tr><td>
<b>Workflow</b>

```bash
python -m provtoolutils.directorywrapper --configfile config.json \
    --agentinfo agent.json --inputdir <workflowinput> --outputdir <workflowoutput> \
    --start 2019-12-30T23:55:00+00:00 --end 2019-12-31T18:16:42+00:00 \
    --activityid $ACTIVITY
```

</td></tr>
</table>

### As Python library

See: [test_exemplary.py](./tests/test_exemplary.py)

### As standalone programm

#### Adding provenance information to file

The standalone programm can be used to create provenance information for non provenance aware files. 

There are two modes: Interactive mode and repository mode. While the first one will ask the user to provide provenance data, the latter one will infer it from a
git repository. The information available will be limited in case of inference but may be enough during development. Do not use the repository mode in
production because it will lack information (like used entities, ...).
**Repository needs to be in a non-dirty state. Otherwise an exception will be thrown.**

##### Repository mode

```
python -m provtoolutils.standalone --repopath <(absolute) path to the local repository root>\
     --filepath <path to the file which should be used, relative to repository root>
```

#### Searching provenance containers based on name

```
python -m provtoolutils.search --entityname testfile2.txt --searchdir tests/test_directorywrapper/integration/
```

### Generating Prov QR codes

The usage of QR codes is helpful, whenever information is presented visually and the corresponding provenance information should be given to the audience. The QR code should be equivalent to the prov file and vice versa. **Nevertheless, in case of changing QR code formats the prov file is leading.**

```
python -m provtoolutils.prov_qr <path to prov file> <path to QR code image file to be generated>
```

**Note: You need [_jabcodeWriter_](https://github.com/jabcode/jabcode) in your path to run the programm.**

<table align="center" border="0"><tr><td align="center" width="9999" border-color="white">
    <img src="../../doc/images/qr_example.png" width="400">
</td></tr>
<tr><td>Example of a QR code containing the provenance information.</td></tr></table>

### Signing provenance container

Provenance container can be signed to include a timestamped signature as well as signing to ensure
approval by a certain person. Both functionalities rely on _openssl_; Windows is currently not
supported, maybe an adaption with WSL is possible.

To sign a container, a request is made to a given timestampserver as well as using a provided
private key to sign the provenance (without signature).

A signed container can be used like a normal one by referencing it based on its content-addressable
id.

```
python -m provtoolutils.sign --provfile <path to provenance file> --private <path to private key of the signer in pem format> --familyname <family name of the signer> --givenname <given name of the signer> --timestampserver <url of the timestamp server>
```

Verify the signature with:

```
openssl ts -verify -in <the value of provtool:timestampsignature> -digest <sha256 hash over provenance without signatures> -CAfile chain.txt
```

You need the certificate chain of the timestamp server. In case of dfn timestamp server, this is
available at: https://pki.pca.dfn.de/dfn-ca-global-g2/pub/cacert/chain.txt.

To determine the sha256 hash you can use jq to remove the signature field of a provenance file:

```
cat <provenance file> | jq 'del(.signature) | jq -c | sha256sum
```
