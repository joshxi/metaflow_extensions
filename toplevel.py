import importlib

import metaflow.plugins
from .plugins.conda import conda_environment, conda_step_decorator


metaflow.plugins.ENVIRONMENTS = metaflow.plugins._merge_lists(
    metaflow.plugins.ENVIRONMENTS, [conda_environment.CondaEnvironment], "TYPE"
)
metaflow.plugins.STEP_DECORATORS = metaflow.plugins._merge_lists(
    metaflow.plugins.STEP_DECORATORS, [conda_step_decorator.CondaStepDecorator], "name"
)

__version__ = None

importlib.reload(metaflow)
