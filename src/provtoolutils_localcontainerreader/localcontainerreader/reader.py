import glob
import json
import jsonschema
import os

from provtoolutils.constants import model_encoding, prov_schema
from provtoolutils.utilities import calculate_data_hash


def read_provanddata(options: dict, cid: str):
    """
    Returns a tuple consisting of the provenance, the _data_ and a boolean with True in case
    of error.
    """
    if 'directory' not in options:
        raise ValueError('Need \'id\' and \'directory\' in the options dict')

    pr = None
    dr = None
    err = False

    globs = glob.glob(f'{os.path.join(options["directory"], "**", cid) + ".prov"}', recursive=True)

    if len(globs) > 0:
        with open(globs[0], 'rb') as f:
            provb = f.read()
            prov = provb.decode(model_encoding)

            if calculate_data_hash(provb) != cid:
                err = True

            prov_obj = json.loads(prov)
            jsonschema.validate(prov_obj, prov_schema)
            datahash = prov_obj['entity']['self']['provtool:datahash']
            rawfile_path = os.path.join(os.path.dirname(globs[0]), datahash)

            pr = provb

            if not os.path.exists(rawfile_path,):
                err = True

                print(f'Data file {rawfile_path} for container {cid} does not exists. Start local search ...')

                bn = os.path.dirname(rawfile_path,)
                for f in os.listdir(bn):
                    fn = os.path.join(bn, f)
                    if not os.path.isfile(fn):
                        continue
                    with open(fn, 'rb') as rf:
                        datab = rf.read()
                        dr = datab

                        if calculate_data_hash(datab) == datahash:
                            err = False
                            break

                return (pr, dr, err)
            with open(rawfile_path, 'rb') as rf:
                datab = rf.read()
                dr = datab

                if calculate_data_hash(datab) != datahash:
                    err = True

    if pr is not None and dr is not None and not err:
        return (pr, dr, False)
    return (pr, dr, True)


def _match(provcontainer_filepath: str, entityname: str):
    try:
        with open(provcontainer_filepath, 'rb') as provcontainer:
            prov_content = provcontainer.read().decode(model_encoding)
            prov = json.loads(prov_content)

            return entityname == next(iter(prov['entity'].values()))['prov:label']
    except Exception as e:
        print(e)
        return False


def search(options: dict, label: str):
    if 'directory' in options:
        entity_filenames = []
        for dirpath, dirnames, filenames in os.walk(options['directory']):
            prov_container_files = [os.path.join(dirpath, f) for f in filenames if f.endswith('.prov')]
            matching = [p for p in prov_container_files if _match(p, label)]

            for m in matching:
                entity_filename = os.path.abspath(m)
                if entity_filename.startswith('./'):
                    entity_filename = entity_filename[2:]

                entity_filenames.append(entity_filename)

        return entity_filenames
    else:
        raise ValueError('Need \'label\' and \'directory\' in the options dict')
