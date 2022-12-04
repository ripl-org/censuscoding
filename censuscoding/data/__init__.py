import os
import pickle
from importlib import resources

from censuscoding.log import log

_lookup_path = None
_lookups = {}

def set_lookup_path():
    """
    Set an alternative path to the directory containing the lookup files
    (e.g. for testing or comparing lookups).
    """
    global _lookup_path
    varname = "CENSUSCODING_DATA"
    if _lookup_path is None and varname in os.environ:
        _lookup_path = os.path.abspath(os.environ[varname])
        log.info(f"using lookup files from", _lookup_path)

def load_lookup(zip2):
    """
    Lazy loading of lookup files by first 2 digits of zip code.
    """
    global _lookups
    if zip2 not in _lookups:
        log.info(f"loading lookup {zip2}")
        if _lookup_path:
            zip2_path = os.path.join(_lookup_path, zip2)
        else:
            with resources.path(__name__, zip2) as p:
                zip2_path = p
        if os.path.exists(zip2_path):
            with open(zip2_path, "rb") as f:
                _lookups[zip2] = pickle.load(f)
        else:
            _lookups[zip2] = {}
    return _lookups[zip2]
