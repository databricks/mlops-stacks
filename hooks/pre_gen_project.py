import cookiecutter

"""
{%- if cookiecutter.cloud == "aws" -%} 
    {{ cookiecutter.update(
        {
            "cloud_specific_node_type_id": "i3.xlarge"
        }
    )}} 
{%- elif cookiecutter.cloud == "azure" -%}
    {{ cookiecutter.update(
            {
                "cloud_specific_node_type_id": "Standard_D3_v2"
            }
        )}}
{% endif %}

{%- if cookiecutter.cicd_platform == "GitHub Actions" -%} 
    {{ cookiecutter.update(
        {
            "cicd_platform": "gitHub"
        }
    )}} 
{%- elif cookiecutter.cicd_platform == "GitHub Actions for GitHub Enterprise Servers" -%}
    {{ cookiecutter.update(
            {
                "cicd_platform": "gitHubEnterprise"
            }
        )}}
{%- elif cookiecutter.cicd_platform == "Azure DevOps" -%}
    {{ cookiecutter.update(
            {
                "cicd_platform": "azureDevOpsServices"
            }
        )}}
{% endif %}

{{ cookiecutter.update(
    {
        "model_name": cookiecutter.project_name + "-model",
        "experiment_base_name": cookiecutter.project_name + "-experiment",
        "service_principal_group": cookiecutter.project_name + "-service-principals",
        "project_name_alphanumeric_underscore": cookiecutter.project_name | regex_replace("[^A-Za-z0-9_-]","") 
            | regex_replace("[-]","_") 
    }
)}}

{%- if "Default: `" in cookiecutter.databricks_staging_workspace_host and cookiecutter.cloud == 'azure' -%}
    {{
        cookiecutter.update({"databricks_staging_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.databricks_staging_workspace_host and cookiecutter.cloud == 'aws' -%}
    {{
        cookiecutter.update({"databricks_staging_workspace_host": "https://your-staging-workspace.cloud.databricks.com" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.databricks_prod_workspace_host and cookiecutter.cloud == 'azure' -%}
    {{
        cookiecutter.update({"databricks_prod_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.databricks_prod_workspace_host and cookiecutter.cloud == 'aws' -%}
    {{
        cookiecutter.update({"databricks_prod_workspace_host": "https://your-prod-workspace.cloud.databricks.com" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.default_branch -%}
    {{
        cookiecutter.update({"default_branch": "main" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.release_branch -%}
    {{
        cookiecutter.update({"release_branch": "release" })
    }}
{% endif %}

{%- if "Default: `" in cookiecutter.read_user_group -%}
    {{
        cookiecutter.update({"read_user_group": "users" })
    }}
{% endif %}

{{
    cookiecutter.update({
        "orig_databricks_prod_workspace_host": cookiecutter.databricks_prod_workspace_host,
        "orig_databricks_staging_workspace_host": cookiecutter.databricks_staging_workspace_host,    
        "databricks_prod_workspace_host": cookiecutter.databricks_prod_workspace_host | get_host,
        "databricks_staging_workspace_host": cookiecutter.databricks_staging_workspace_host | get_host,        
    })
}}
"""


def validate_cookiecutter_version(version_string):
    cookiecutter_version_components = version_string.split(".")
    major_version = int(cookiecutter_version_components[0])
    minor_version = int(cookiecutter_version_components[1])
    if not (major_version > 2 or (major_version == 2 and minor_version >= 1)):
        raise ValueError(
            f"Cookiecutter version is not at least 2.1.0. Got version {version_string}."
        )


def validate_databricks_workspace_host(host, orig_host):
    if not host.startswith("https://"):
        raise ValueError(
            f"Databricks workspace host URLs must start with https. Got invalid workspace host {orig_host}."
        )


INVALID_PROJECT_NAME_CHARS = {" ", "\\", "/", "."}
VALID_PROJECT_NAME_MSG = (
    "Valid project names must contain at least three alphanumeric characters and "
    "cannot contain any of the following characters: %s" % INVALID_PROJECT_NAME_CHARS
)


def validate_root_dir(root_dir):
    invalid_chars_in_name = INVALID_PROJECT_NAME_CHARS.intersection(root_dir)
    if len(invalid_chars_in_name) > 0:
        raise ValueError(
            f"Root directory '{root_dir}' contained invalid characters {invalid_chars_in_name}. {VALID_PROJECT_NAME_MSG}"
        )


def validate_project_name(project_name):
    invalid_chars_in_name = INVALID_PROJECT_NAME_CHARS.intersection(project_name)
    if len(invalid_chars_in_name) > 0:
        raise ValueError(
            f"Project name '{project_name}' contained invalid characters {invalid_chars_in_name}. {VALID_PROJECT_NAME_MSG}"
        )


def validate_alphanumeric_project_name(project_name, alphanumeric_project_name):
    if len(alphanumeric_project_name) < 3:
        raise ValueError(
            f"Project name '{project_name}' was too short. {VALID_PROJECT_NAME_MSG}"
        )


def validate_feature_store(use_feature_store, cicd_platform):
    if use_feature_store == "yes" and cicd_platform == "azureDevOpsServices":
        raise RuntimeError(
            "Feature Store component with Azure DevOps CI/CD is not supported yet. "
            "Please use Github Actions instead, if possible."
        )


def validate_cloud_cicd_platform(cloud, cicd_platform):
    if cloud == "aws" and cicd_platform == "azureDevOpsServices":
        raise RuntimeError(
            "Azure DevOps is not supported as a cicd_platform option with cloud=aws. "
            "If cloud=aws the currently supported cicd_platform is GitHub Actions."
        )


if __name__ == "__main__":
    validate_cookiecutter_version(cookiecutter.__version__)
    orig_databricks_staging_workspace_host = (
        "{{cookiecutter.orig_databricks_staging_workspace_host}}"
    )
    orig_databricks_prod_workspace_host = (
        "{{cookiecutter.orig_databricks_prod_workspace_host}}"
    )
    databricks_staging_workspace_host = (
        "{{cookiecutter.databricks_staging_workspace_host}}"
    )
    databricks_prod_workspace_host = "{{cookiecutter.databricks_prod_workspace_host}}"
    for host, orig_host in [
        (databricks_staging_workspace_host, orig_databricks_staging_workspace_host),
        (databricks_prod_workspace_host, orig_databricks_prod_workspace_host),
    ]:
        validate_databricks_workspace_host(host, orig_host)
    validate_project_name("{{cookiecutter.project_name}}")
    validate_root_dir("{{cookiecutter.root_dir__update_if_you_intend_to_use_monorepo}}")
    validate_alphanumeric_project_name(
        "{{cookiecutter.project_name}}", "{{cookiecutter.project_name_alphanumeric_underscore}}"
    )
    validate_cloud_cicd_platform(
        "{{cookiecutter.cloud}}", "{{cookiecutter.cicd_platform}}"
    )
    validate_feature_store(
        "{{cookiecutter.include_feature_store}}", "{{cookiecutter.cicd_platform}}"
    )
