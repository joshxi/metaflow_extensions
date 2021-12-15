from .conda.conda_environment import CondaEnvironment
from .conda.conda_flow_decorator import CondaFlowDecorator
from .conda.conda_step_decorator import CondaStepDecorator


def get_plugin_cli():
    """ metaflow_extensions currently does not provide additional CLIs """
    return []


ENVIRONMENTS = [CondaEnvironment]
FLOW_DECORATORS = [CondaFlowDecorator]
LOGGING_SIDECARS = {}
METADATA_PROVIDERS = []
MONITOR_SIDECARS = {}
SIDECARS = {}
STEP_DECORATORS = [CondaStepDecorator]
