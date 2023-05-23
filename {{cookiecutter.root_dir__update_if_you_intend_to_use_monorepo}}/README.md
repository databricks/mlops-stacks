# {{cookiecutter.root_dir__update_if_you_intend_to_use_monorepo}}

This directory contains an ML project based on the default
[Databricks MLOps Stack](https://github.com/databricks/mlops-stack),
defining a production-grade ML pipeline for automated retraining and batch inference of an ML model on tabular data.

See the [Project overview](docs/project-overview.md) for details on the ML pipeline and code structure
in this repo.

## Using this repo

The table below links to detailed docs explaining how to use this repo for different use cases.

If you're a data scientist just getting started with this repo for a brand new ML project, we recommend starting with
the [Project overview](docs/project-overview.md) and
{% if cookiecutter.include_feature_store == "yes" %}[ML quickstart](docs/ml-developer-guide-fs.md).
{% else %}[ML quickstart](docs/ml-developer-guide.md).{% endif %}

When you're satisfied with initial ML experimentation (e.g. validated that a model with reasonable performance can be
trained on your dataset) and ready to deploy production training/inference
pipelines, ask your ops team to follow the [MLOps setup guide](docs/mlops-setup.md) to configure CI/CD and deploy 
production ML pipelines.

After that, follow the [ML pull request guide](docs/ml-pull-request.md)
and [ML resource config guide]({{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md) to propose, test, and deploy changes to production ML code (e.g. update model parameters)
or pipeline resources (e.g. use a larger instance type for model training) via pull request.

| Role                          | Goal                                                                         | Docs                                                                                                                                                                |
|-------------------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| First-time users of this repo | Understand the ML pipeline and code structure in this repo                   | [Project overview](docs/project-overview.md)                                                                                                                        |
| Data Scientist                | Get started writing ML code for a brand new project                          | {% if cookiecutter.include_feature_store == "yes" %}[ML quickstart](docs/ml-developer-guide-fs.md).{% else %}[ML quickstart](docs/ml-developer-guide.md){% endif %} |
| Data Scientist                | Update production ML code (e.g. model training logic) for an existing project | [ML pull request guide](docs/ml-pull-request.md)                                                                                                                    |
| Data Scientist                | Modify production model ML resources, e.g. model training or inference jobs  | [ML resource config guide]({{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md)                                                     |
| MLOps / DevOps                | Set up CI/CD for the current ML project   | [MLOps setup guide](docs/mlops-setup.md)                                                                                                                            |

## Monorepo

It's possible to use the repo as a monorepo that contains multiple projects. All projects share the same workspaces and service principals.

For example, assuming there's existing repo with root directory name `monorepo_root_dir` and project name `project1`
1. Create another project from cookiecutter with project name `project2` and root directory name `project2`.
2. Copy the internal directory `project2/project2` to root directory of existing repo `monorepo_root_dir/project2`.
{% if cookiecutter.cicd_platform in ["gitHub", "gitHubEnterprise"] -%}
3. Copy yaml files from `project2/.github/workflows/` to `monorepo_root_dir/.github/workflows/` and make sure there's no name conflicts.
{% endif -%}
{%- if cookiecutter.cicd_platform == "azureDevOpsServices" %}
3. Copy yaml files from `project2/.azure/devops-pipelines/` to `monorepo_root_dir/.azure/devops-pipelines/` and make sure there's no name conflicts.
{% endif -%}

