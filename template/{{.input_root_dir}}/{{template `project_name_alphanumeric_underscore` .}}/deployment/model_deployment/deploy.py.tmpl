import sys
from mlflow import MlflowClient

def deploy(model_uri, env):
    """Deploys an already-registered model in Unity catalog by assigning it the appropriate alias for model deployment.

    :param model_uri: URI of the model to deploy. Must be in the format "models:/<name>/<version-id>", as described in
                      https://www.mlflow.org/docs/latest/model-registry.html#fetching-an-mlflow-model-from-the-model-registry
    :param env: name of the environment in which we're performing deployment, i.e one of "dev", "staging", "prod".
                Defaults to "dev"
    :return:
    """
    print(f"Deployment running in env: {env}")
    _, model_name, version = model_uri.split("/")
    client = MlflowClient()
    mv = client.get_model_version(model_name, version)
    target_alias = "champion"
    if target_alias not in mv.aliases:
        client.set_registered_model_alias(
            name=model_name,
            alias=target_alias,
            version=version)
        print(f"Assigned alias '{target_alias}' to model version {model_uri}.")

        # remove "challenger" alias if assigning "champion" alias
        if target_alias == "champion" and "challenger" in mv.aliases:
            print(f"Removing 'challenger' alias from model version {model_uri}.")
            client.delete_registered_model_alias(
                name=model_name,
                alias="challenger")


if __name__ == "__main__":
    deploy(model_uri=sys.argv[1], env=sys.argv[2])
