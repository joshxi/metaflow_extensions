import errno
import os
import fcntl

import yaml

from metaflow_extensions.constants import CONDA_MAGIC_FILE


def get_conda_manifest_path(ds_root, flow_name):
    return os.path.join(ds_root, flow_name, CONDA_MAGIC_FILE)


def read_conda_manifest(ds_root, flow_name):
    path = get_conda_manifest_path(ds_root, flow_name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path) as f:
            return yaml.safe_load(f)
    else:
        return {}


def write_to_conda_manifest(ds_root, flow_name, key, value):
    path = get_conda_manifest_path(ds_root, flow_name)
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as x:
        if x.errno != errno.EEXIST:
            raise
    with os.fdopen(os.open(path, os.O_RDWR | os.O_CREAT), "r+") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            data = {}
            if os.path.getsize(path) > 0:
                f.seek(0)
                data = yaml.safe_load(f)
            data[key] = value
            f.seek(0)
            yaml.safe_dump(data, f)
            f.truncate()
        except IOError as e:
            if e.errno != errno.EAGAIN:
                raise
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
