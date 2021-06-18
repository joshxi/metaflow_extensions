import tempfile

import metaflow.plugins.conda.conda as mf_conda
import yaml


class Conda(mf_conda.Conda):
    def create(
        self,
        step_name,
        env_id,
        env_dict,
        architecture=None,
        disable_safety_checks=False,
    ):
        # Create the conda environment
        try:
            with mf_conda.CondaLock(self._env_lock_file(env_id)):
                self._remove(env_id)
                self._create(
                    env_id,
                    env_dict,
                    architecture=architecture,
                    disable_safety_checks=disable_safety_checks,
                )
        except mf_conda.CondaException as e:
            raise mf_conda.CondaStepException(e, step_name)

    def _create(self, env_id, env_dict, architecture=None, disable_safety_checks=False):
        with tempfile.TemporaryDirectory() as tmp_dir:
            conda_env_yaml = f"{tmp_dir}/conda.yaml"
            with open(conda_env_yaml, "w") as f:
                yaml.safe_dump(env_dict, f)
            cmd = [
                "env",
                "create",
                "--name",
                env_id,
                "--file",
                conda_env_yaml,
                "--quiet",
            ]
            self._call_conda(
                cmd,
                architecture=architecture,
                disable_safety_checks=disable_safety_checks,
            )
