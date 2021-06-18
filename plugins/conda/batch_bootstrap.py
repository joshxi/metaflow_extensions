import os
import shutil
import sys
import tempfile

from metaflow.metaflow_config import DATASTORE_LOCAL_DIR
import yaml

from . import CONDA_MAGIC_FILE


def setup_conda_manifest(flow_name):
    manifest_folder = os.path.join(os.getcwd(), DATASTORE_LOCAL_DIR, flow_name)
    if not os.path.exists(manifest_folder):
        os.makedirs(manifest_folder)
    shutil.move(
        os.path.join(os.getcwd(), CONDA_MAGIC_FILE),
        os.path.join(manifest_folder, CONDA_MAGIC_FILE),
    )
    return os.path.join(os.getcwd(), DATASTORE_LOCAL_DIR, flow_name)


def bootstrap_environment(flow_name, env_id):
    install_conda_cmds = "if ! type conda  >/dev/null 2>&1; \
            then wget -q https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh; \
            sh Miniconda3-latest-Linux-x86_64.sh -b -p miniconda3 >/dev/null 2>&1; \
            . miniconda3/bin/activate base; fi"
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_folder = setup_conda_manifest(flow_name)
        with open(os.path.join(manifest_folder, CONDA_MAGIC_FILE)) as f:
            cached_deps = yaml.safe_load(f)
        conda_yaml_path = os.path.join(tmp_dir, "conda.yaml")
        with open(conda_yaml_path, "w") as f:
            yaml.safe_dump(cached_deps[env_id], f)
        conda_env_path = os.path.join(os.getcwd(), env_id)
        args = [
            "if ! type wget >/dev/null 2>&1; \
            then apt-get -qq -y install wget >/dev/null 2>&1; fi",
            install_conda_cmds,
            "cd {0}".format(os.getcwd()),
            "conda env create -f {0} -p {1} >/dev/null 2>&1".format(
                conda_yaml_path, conda_env_path
            ),
            f"conda activate {conda_env_path}; conda list",
        ]
        os.system(" && ".join(args))


if __name__ == "__main__":
    bootstrap_environment(sys.argv[1], sys.argv[2])
