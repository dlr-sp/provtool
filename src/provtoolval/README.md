#  Provtoolval

[[_TOC_]]

This package contains a framework for validation of _provenance container_ files.

The provenance chain of a given entity is valid, if the files of all _used_ relations can be successfully retrieved and loaded. The entities itself may be stored remotely,
in which case some method of data gathering is necessary.

There may be multiple locations at which entities are stored. Different locations need to be supported with corresponding _provenance container_ reader plugin (see for example [src/localfile](src/localfile/README.md)).

## Requirements

- Python 3.8+

## Installation & upgrade

Create a virtualenv for your project. Make sure, git is installed on your machine and you have a valid account for the repository.

Go to the repository [tags](https://github.com/dlr-sp/provtool/-/tags) and lookup the latest provtoolval tag.

Activate your virtual environment and install [provtoolutils](../utils/README.md) and one of the _provenance container_ reader (for example [../localcontainer/README](../localcontainer/README)).

Install via (replace {username} with your repository user and {tag} with the tagname you want to install) the following command. **Please remove any old version before. Please use a current version of the provtoolutils.**

```
pip install "git+https://{username}@github.com/dlr-sp/provtool.git@{tag}#egg=provtoolval&subdirectory=src/validation"
```

**Example**:

```
pip install "git+https://max_mu@github.com/dlr-sp/provtool.git@provtoolval_0.1.0#egg=provtoolval&subdirectory=src/validation"
```

To verify a correct installation, type

```
pip show provtoolval
```

## Building from source

Checkout the project and run:

```bash
cd provtool/src/provtoolval
pip install -e .
```

## Test

Checkout the project and run:

```bash
cd provtool/src/provtoolval
tox
```

Many of the tests use a test directory containing reference data. The approach for using the reference data is similar to https://stackoverflow.com/a/29631801.

## Usage

### Simple usage

There are some scripts provided for recurring simple validation tasks on provenance container. These script are not tuned for performance. If you would like to do some more advanced analysis of provenance graphs see below and alternatively think about using a graph database where the provenance extracted from the container is stored and can be analysed easily.

#### List input of activity chains

Assume there is a process which involves multiple activities which use data from each other and provide data to each other too. In this setting you want to track the data from the final result back to the input files. This can be done easily:

```bash
python -m provtoolval.list_origin --location <absolute path to the directory, where ALL container from the process are stored> --output <(relative) path to the output file (csv)>
```

The resulting output file contains a csv table which lists the file name, the container id, the activities and timestamps for the basic input files.

**This script is not optimized for performance. For example: A data set with 11GB distributed over 1505 files may take 20min on a descent machine. These numbers may vary for your use case.**

### Advanced usage

#### Container reader

You can provide your own container reader to collect _provenance container_ for validation from different sources. Currently, only file based lookup is supported, but this can be extended in _provtoolval.validator.Validator#read_provanddata_. To register your own reader, provide a _read_provanddata_ function in a module, which is registered with the _provtoolutils.reader_ entrypoint. See  [src/localfile](src/localfile/README.md) as an example).

#### Running

The validation tool can create html and csv reports. While the former is nice for documentation, the latter is useful for analysis of the artefacts. Which type
is generated is determined by the file ending of the report file, which could be either html or csv. Up to now, only file based container search is supported.

```bash
python -m provtoolval.main --filelocation <directory to search for the container> --target <target hash id> --reportfile /home/.../report.html
```

As result of the process, a html report (validation\_report.html) is created in the current working directory.
