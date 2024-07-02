import os
import subprocess
import json
import requests

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        print(f"Error: {err.decode('utf-8')}")
        exit(process.returncode)
    print(out.decode('utf-8'))

def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"The environment variable {name} is missing")
    return value

def create_github_repo(token, org, repo_name, description):
    url = f"https://api.github.com/orgs/{org}/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": True
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 201:
        print(f"Error creating GitHub repository: {response.text}")
        exit(1)
    return response.json()["clone_url"]

def create_mlops_project(settings_path):
    with open(settings_path, "r") as f:
        params = json.load(f)

    project_name = params["project_name"]
    project_description = params["project_description"]
    cloud_provider = params["cloud_provider"]
    cicd_platform = params["cicd_platform"]
    staging_workspace = params["staging_workspace"]
    prod_workspace = params["prod_workspace"]
    default_branch = params["default_branch"]
    release_branch = params["release_branch"]
    root_dir = params["root_dir"]
    read_user_group = params["read_user_group"]
    include_models_in_unity_catalog = params["include_models_in_unity_catalog"]
    schema_name = params["schema_name"]
    unity_catalog_read_user_group = params["unity_catalog_read_user_group"]
    include_feature_store = params["include_feature_store"]
    include_mlflow_recipes = params["include_mlflow_recipes"]
    github_token = get_env_variable("GITHUB_TOKEN")
    github_org = get_env_variable("GITHUB_ORG")

    # Initialize new MLOps project
    init_command = f"""
    databricks bundle init mlops-stacks \
      --input_project_name="{project_name}" \
      --input_cloud="{cloud_provider}" \
      --input_cicd_platform="{cicd_platform}" \
      --input_databricks_staging_workspace_host="{staging_workspace}" \
      --input_databricks_prod_workspace_host="{prod_workspace}" \
      --input_default_branch="{default_branch}" \
      --input_release_branch="{release_branch}" \
      --input_root_dir="{root_dir}" \
      --input_read_user_group="{read_user_group}" \
      --input_include_models_in_unity_catalog="{include_models_in_unity_catalog}" \
      --input_schema_name="{schema_name}" \
      --input_unity_catalog_read_user_group="{unity_catalog_read_user_group}" \
      --input_include_feature_store="{include_feature_store}" \
      --input_include_mlflow_recipes="{include_mlflow_recipes}"
    """
    run_command(init_command)

    # Create GitHub repository
    repo_url = create_github_repo(github_token, github_org, project_name, project_description)
    print(f"New Project Git URL: {repo_url}")

    # Set up the new project
    setup_commands = f"""
    git clone {repo_url} new-project
    cp -r ./* new-project/
    cd new-project
    git add .
    git commit -m "Initial commit from template"
    git push origin master
    """
    run_command(setup_commands)

def main():
    projects_dir = "projects"
    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        settings_path = os.path.join(project_path, "settings.json")
        if os.path.isfile(settings_path):
            print(f"Creating project: {project_name}")
            create_mlops_project(settings_path)

if __name__ == "__main__":
    main()
