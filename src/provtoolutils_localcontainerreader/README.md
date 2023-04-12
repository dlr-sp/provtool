# Local container locator

[[_TOC_]]

This plugin provides functionality to search and read local _provenance container_.

## How it works

The plugin uses a given provenance file, extracts the _data_ hash and opens the file with the corresponding hash. If such a file does not exists, it calculates the hash sum of all files in the same directory like the provenance file; in case of a match, this file is used as _data_. It performs the necessary checks to make sure, the _provenance container_ is valid. If something goes wrong, an error is indicated.

The plugin is registered via the [python entrypoints](https://packaging.python.org/en/latest/specifications/entry-points/) to the group _provtoolutils.reader_. The plugin is registered with the name _file_ to indicate its ability to read local file-base _provenance container_.

## Installation

```
pip install --upgrade "git+https://{username}@github.com/dlr-sp/provtool.git@{tag}#egg=provtoolutils_localcontainerreader&subdirectory=src/provtoolutils_localcontainerreader"
```

**Example**:

```
pip install --upgrade "git+https://max_mu@github.com/dlr-sp/provtool.git@provtoolutils_localcontainerreader_0.4.1#egg=provtoolutils_localcontainerreader&subdirectory=src/provtoolutils_localcontainerreader"
```

## Testing

Checkout the project and run:

```bash
cd provtool/src/provtoolutils_localcontainerreader
tox
```

Many of the tests use a test directory containing reference data. The approach for using the reference data is similar to https://stackoverflow.com/a/29631801.

## How to use

Install [provtoolutils](../utils/README.md) and the local container locator plugin (see above). Afterwards, each provtoolutils functionality, can make use of this plugin and therefore deal with local container.
