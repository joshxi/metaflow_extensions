import json
import os
import tarfile

import metaflow.plugins.conda.conda_environment as mf_conda_env
import yaml

from . import CONDA_MAGIC_FILE, get_conda_manifest_path


class CondaEnvironment(mf_conda_env.CondaEnvironment):
    TYPE = "conda"
    _filecache = None

    def bootstrap_commands(self, step_name):
        from metaflow.mflog import BASH_SAVE_LOGS

        # Bootstrap conda and execution environment for step
        env_id = self._get_env_id(step_name)
        if env_id is not None:
            return [
                "mflog 'Bootstrapping environment...'",
                BASH_SAVE_LOGS,
                'python -m metaflow_extensions.batch_bootstrap.conda "%s" %s'
                % (self.flow.name, env_id),
                "mflog 'Environment bootstrapped.'",
                BASH_SAVE_LOGS,
            ]
        return []

    def add_to_package(self):
        files = self.base_env.add_to_package()
        # Add conda manifest file to job package at the top level.
        path = get_conda_manifest_path(self.local_root, self.flow.name)
        if os.path.exists(path):
            files.append((path, os.path.basename(path)))
        return files

    @classmethod
    def get_client_info(cls, flow_name, metadata):
        from metaflow.client.filecache import FileCache

        if cls._filecache is None:
            cls._filecache = FileCache()
        info = metadata.get("code-package")
        env_id = metadata.get("conda_env_id")
        if info is None or env_id is None:
            return {"type": "conda"}
        info = json.loads(info)
        with cls._filecache.get_data(info["ds_type"], flow_name, info["sha"]) as f:
            tar = tarfile.TarFile(fileobj=f)
            conda_file = tar.extractfile(CONDA_MAGIC_FILE)
            if conda_file is None:
                return {"type": "conda"}
            info = yaml.safe_load(conda_file.read().decode("utf-8"))
        new_info = {"type": "conda", "deps": info[env_id]["dependencies"]}
        return new_info

    def get_package_commands(self, code_package_url):
        pkg_cmds = self.base_env.get_package_commands(code_package_url)
        pkg_cmds.append(f"{self._python()} -m pip install pyyaml -qqq")
        return pkg_cmds
