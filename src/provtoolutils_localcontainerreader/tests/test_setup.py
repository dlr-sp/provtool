import importlib
import sys
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points
from types import FunctionType, ModuleType

def test_entrypoints():
    discovered_plugins = entry_points(group='provtoolutils.reader')
    assert len(discovered_plugins) > 0
    assert 'file' in [p.name for p in discovered_plugins]

    assert isinstance(discovered_plugins['file'].load(), ModuleType)

    f = getattr(discovered_plugins['file'].load(), 'read_provanddata')
    assert isinstance(f, FunctionType)
