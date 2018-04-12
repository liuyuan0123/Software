import os
from tempfile import mkdtemp, NamedTemporaryFile

from .logging_logger import logger

from .contracts_ import contract
from .exception_utils import raise_desc
from .yaml_pretty import yaml_load
from .constants import DuckietownConstants

from contextlib import contextmanager


def mkdirs_thread_safe(dirname):
    from compmake.utils.filesystem_utils import mkdirs_thread_safe as md
    return md(dirname)

@contract(s=str, returns=str)
def dir_from_data(s):
    data = yaml_load(s)
    d = create_tmpdir()
    write_to_dir(data, d)
    return d

def write_to_dir(data, d):
    if isinstance(data, dict):
        if not os.path.exists(d):
            os.makedirs(d)
        for k, v in data.items():
            write_to_dir(v, os.path.join(d, k))
    elif isinstance(data, str):
        with open(d, 'w') as f:
            f.write(data)
        logger.info('Wrote %s' % d)
    else:
        msg = 'Invalid type.'
        raise_desc(ValueError, msg, data=data, d=d)


def get_dt_tmp_dir():
    """ Returns *the* temp dir for this project.
    Note that we need to customize with username, otherwise
    there will be permission problems.  """
    V = DuckietownConstants.DUCKIETOWN_TMP_variable
    if V in os.environ:
        return os.environ[V]
    from tempfile import gettempdir
    d0 = gettempdir()
    import getpass
    username = getpass.getuser()
    d = os.path.join(d0, 'tmpdir-%s' % username)
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError:
            pass
    return d

def create_tmpdir(prefix='tmpdir'):
    base = get_dt_tmp_dir()
    if not os.path.exists(base):
        mkdirs_thread_safe(base)

    d = mkdtemp(dir=base, prefix=prefix)
    return d

@contextmanager
def tmpfile(suffix):
    ''' Yields the name of a temporary file '''
    temp_file = NamedTemporaryFile(suffix=suffix)
    yield temp_file.name
    temp_file.close()
