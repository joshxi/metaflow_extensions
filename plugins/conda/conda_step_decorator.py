from hashlib import sha1

import metaflow.plugins.conda.conda_step_decorator as mf_conda
import yaml

from .conda import Conda
from . import read_conda_manifest, write_to_conda_manifest


class CondaStepDecorator(mf_conda.CondaStepDecorator):
    """
    Conda decorator that sets the Conda environment for your step

    To use, add this decorator to your step:
    ```
    @conda
    @step
    def MyStep(self):
        ...
    ```

    Information in this decorator will override any eventual @conda_base flow level decorator.
    Parameters
    ----------
    libraries : Dict
        Libraries to use for this step. The key is the name of the package and the value
        is the version to use. Defaults to {}
    pip : Dict
        Pip packages to install for this step. The key is the name of the package and the 
        value is the version to use. Defaults to {}
    python : string
        Version of Python to use (for example: '3.7.4'). Defaults to None
        (will use the current python version)
    disabled : bool
        If set to True, disables Conda. Defaults to False
    """

    name = "conda"
    conda = None
    environments = None
    defaults = {"libraries": {}, "pip": {}, "python": None, "disabled": None}

    def _step_deps(self):
        from metaflow.metaflow_config import get_pinned_conda_libs

        deps = [f"python=={self._python_version()}", "pyyaml==5.4.1"]
        # Get base conda libraries and pip requirements
        conda_libs = get_pinned_conda_libs(self._python_version())
        conda_libs.update(self.base_attributes["libraries"])
        pip_pkgs = self.base_attributes["pip"].copy()
        # Get and parse if necessary conda libraries and pip requirements for the step
        conda_libs.update(
            yaml.safe_load(self.attributes["libraries"])
            if isinstance(self.attributes["libraries"], str)
            else self.attributes["libraries"]
        )
        pip_pkgs.update(
            yaml.safe_load(self.attributes["pip"])
            if isinstance(self.attributes["pip"], str)
            else self.attributes["pip"]
        )
        # Prioritize pip packages over conda dependencies
        conda_libs = {k: v for k, v in conda_libs.items() if k not in pip_pkgs}
        # Convert conda dependencies to a list of pinned pkgs
        conda_libs_list = [f"{k}=={v}" for k, v in conda_libs.items()]
        if "pip" not in conda_libs:
            conda_libs_list.append("pip")
        deps.extend(sorted(conda_libs_list))
        deps.append({"pip": sorted([f"{k}=={v}" for k, v in pip_pkgs.items()])})
        return deps

    def _env_id(self):
        deps = self._step_deps()
        return "metaflow_%s_%s_%s" % (
            self.flow.name,
            self.architecture,
            sha1(yaml.safe_dump(deps).encode("utf-8")).hexdigest(),
        )

    def _prepare_step_environment(self, step_name, ds_root):
        env_id = self._env_id()
        cached_deps = read_conda_manifest(ds_root, self.flow.name)
        if CondaStepDecorator.conda is None:
            CondaStepDecorator.conda = Conda()
            CondaStepDecorator.environments = CondaStepDecorator.conda.environments(
                self.flow.name
            )
        if env_id not in cached_deps or env_id not in CondaStepDecorator.environments:
            deps = self._step_deps()
            env_dict = {
                "channels": self.conda.config()["channels"],
                "dependencies": deps,
            }
            self.conda.create(
                self.step,
                env_id,
                env_dict,
                architecture=self.architecture,
                disable_safety_checks=self.disable_safety_checks,
            )
            CondaStepDecorator.environments = CondaStepDecorator.conda.environments(
                self.flow.name
            )
            write_to_conda_manifest(ds_root, self.flow.name, env_id, env_dict)
        return env_id
