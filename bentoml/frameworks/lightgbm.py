import os

from bentoml.service.artifacts import BentoServiceArtifact
from bentoml.exceptions import MissingDependencyException, InvalidArgument
from bentoml.service.env import BentoServiceEnv


class LightGBMModelArtifact(BentoServiceArtifact):
    """
    Abstraction for save/load object with LightGBM.

    Args:
        name (string): name of the artifact
        model_extension (string): Extension name for saved xgboost model

    Raises:
        MissingDependencyException: lightgbm package is required for using
            LightGBMModelArtifact
        InvalidArgument: invalid argument type, model being packed must be instance of
            lightgbm.Booster

    Example usage:

    >>> import lightgbm as lgb
    >>> # Prepare data
    >>> train_data = lgb.Dataset(...)
    >>> # train model
    >>> model = lgb.train(train_set=train_data, ...)
    >>>
    >>> import bentoml
    >>> from bentoml.frameworks.lightgbm import LightGBMModelArtifact
    >>> from bentoml.adapters import DataframeInput
    >>>
    >>> @bentoml.artifacts([LightGBMModelArtifact('model')])
    >>> @bentoml.env(infer_pip_packages=True)
    >>> class LgbModelService(bentoml.BentoService):
    >>>
    >>>     @bentoml.api(input=DataframeInput())
    >>>     def predict(self, df):
    >>>         return self.artifacts.model.predict(df)
    >>>
    >>> svc = LgbModelService()
    >>> svc.pack('model', model)
    """

    def __init__(self, name, model_extension=".txt"):
        super(LightGBMModelArtifact, self).__init__(name)
        self.model_extension = model_extension
        self._model = None

    def _model_file_path(self, base_path):
        return os.path.join(base_path, self.name + self.model_extension)

    def pack(self, model):  # pylint:disable=arguments-differ
        try:
            import lightgbm as lgb
        except ImportError:
            raise MissingDependencyException(
                "lightgbm package is required to use LightGBMModelArtifact"
            )

        if not isinstance(model, lgb.Booster):
            raise InvalidArgument(
                "Expect `model` argument to be a `lightgbm.Booster` instance"
            )

        self._model = model
        return self

    def load(self, path):
        try:
            import lightgbm as lgb
        except ImportError:
            raise MissingDependencyException(
                "lightgbm package is required to use LightGBMModelArtifact"
            )
        bst = lgb.Booster(model_file=self._model_file_path(path))

        return self.pack(bst)

    def set_dependencies(self, env: BentoServiceEnv):
        env.add_pip_packages(['lightgbm'])

    def save(self, dst):
        return self._model.save_model(self._model_file_path(dst))

    def get(self):
        return self._model