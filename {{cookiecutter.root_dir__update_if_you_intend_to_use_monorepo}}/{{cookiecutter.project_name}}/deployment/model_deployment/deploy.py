from utils import get_deployed_model_stage_for_env
from mlflow.tracking import MlflowClient
import sys


def deploy(model_uri, env):
    """
    Deploys an already-registered model produced by moving it into the appropriate stage for model deployment.

    :param model_uri: URI of the model to deploy. Must be in the format "models:/<name>/<version-id>", as described in
                      https://www.mlflow.org/docs/latest/model-registry.html#fetching-an-mlflow-model-from-the-model-registry
    :param env: name of the environment in which we're performing deployment, i.e one of "dev", "staging", "prod".
                Defaults to "dev"
    :return:
    """
    _, model_name, version = model_uri.split("/")
    client = MlflowClient()
    mv = client.get_model_version(model_name, version)
    target_stage = get_deployed_model_stage_for_env(env)
    if mv.current_stage != target_stage:
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=target_stage,
            archive_existing_versions=True,
        )
    print(f"Successfully deployed model with URI {model_uri} to {env}")


if __name__ == "__main__":
    deploy(model_uri=sys.argv[1], env=sys.argv[2])
