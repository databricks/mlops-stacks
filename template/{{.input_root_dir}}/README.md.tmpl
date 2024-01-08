# {{ template `root_dir` .}}

This directory contains an ML project based on the default
[Databricks MLOps Stacks](https://github.com/databricks/mlops-stacks),
defining a production-grade ML pipeline for automated retraining and batch inference of an ML model on tabular data.

See the full pipeline structure below. The [MLOps Stacks README](https://github.com/databricks/mlops-stacks/blob/main/Pipeline.md)
contains additional details on how ML pipelines are tested and deployed across each of the dev, staging, prod environments below.

![MLOps Stacks diagram](docs/images/mlops-stack-summary.png)


## Code structure
This project contains the following components:

| Component                  | Description                                                                                                                                                                                                                                                                                                                                             |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ML Code                    | Example ML project code, with unit tested Python modules and notebooks                                                                                                                                                                                                                                                                                  |
| ML Assets as Code | ML pipeline assets (training and batch inference jobs with schedules, etc) configured and deployed through [databricks CLI bundles]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/cli/bundle-cli.html")) }})                                                                                              |
| CI/CD                      | {{ if (eq .input_cicd_platform `github_actions`) }}[GitHub Actions](https://github.com/actions) workflows to test and deploy ML code and assets {{ else if (eq .input_cicd_platform `azure_devops`) }}[Azure DevOps Pipelines](https://azure.microsoft.com/en-gb/products/devops/pipelines/) to test and deploy ML code and assets{{ end }}      |

contained in the following files:

```
{{ template `root_dir` .}}        <- Root directory. Both monorepo and polyrepo are supported.
│
├── {{template `project_name_alphanumeric_underscore` .}}       <- Contains python code, notebooks and ML assets related to one ML project. 
│   │
│   ├── requirements.txt        <- Specifies Python dependencies for ML code (for example: model training, batch inference).
│   │
│   ├── databricks.yml          <- databricks.yml is the root bundle file for the ML project that can be loaded by databricks CLI bundles. It defines the bundle name, workspace URL and asset config component to be included.
│   │
{{ if and (eq .input_include_feature_store `no`) (eq .input_include_mlflow_recipes `no`) -}}
│   ├── training                <- Training folder contains Notebook that trains and registers the model.
│   │
│   ├── validation              <- Optional model validation step before deploying a model.
│   │
│   ├── monitoring              <- Model monitoring, feature monitoring, etc.
│   │
│   ├── deployment              <- Deployment and Batch inference workflows
│   │   │
│   │   ├── batch_inference     <- Batch inference code that will run as part of scheduled workflow.
│   │   │
│   │   ├── model_deployment    <- As part of CD workflow, deploy the registered model by assigning it the appropriate alias.
│   │
│   │
│   ├── tests                   <- Unit tests for the ML project, including the modules under `features`.
│   │
│   ├── assets               <- ML asset (ML jobs, MLflow models) config definitions expressed as code, across dev/staging/prod/test.
│       │
│       ├── model-workflow-asset.yml                <- ML asset config definition for model training, validation, deployment workflow
│       │
│       ├── batch-inference-workflow-asset.yml      <- ML asset config definition for batch inference workflow
│       │
│       ├── ml-artifacts-asset.yml                  <- ML asset config definition for model and experiment
│       │
│       ├── monitoring-workflow-asset.yml           <- ML asset config definition for data monitoring workflow
{{ else if (eq .input_include_feature_store `yes`) -}}
│   ├── training                <- Training folder contains Notebook that trains and registers the model with feature store support.
│   │
│   ├── feature_engineering     <- Feature computation code (Python modules) that implements the feature transforms.
│   │                              The output of these transforms get persisted as Feature Store tables. Most development
│   │                              work happens here.
│   │
│   ├── validation              <- Optional model validation step before deploying a model.
│   │
│   ├── monitoring              <- Model monitoring, feature monitoring, etc.
│   │
│   ├── deployment              <- Deployment and Batch inference workflows
│   │   │
│   │   ├── batch_inference     <- Batch inference code that will run as part of scheduled workflow.
│   │   │
│   │   ├── model_deployment    <- As part of CD workflow, deploy the registered model by assigning it the appropriate alias.
│   │
│   │
│   ├── tests                   <- Unit tests for the ML project, including the modules under `features`.
│   │
│   ├── assets               <- ML asset (ML jobs, MLflow models) config definitions expressed as code, across dev/staging/prod/test.
│       │
│       ├── model-workflow-asset.yml                <- ML asset config definition for model training, validation, deployment workflow
│       │
│       ├── batch-inference-workflow-asset.yml      <- ML asset config definition for batch inference workflow
│       │
│       ├── feature-engineering-workflow-asset.yml  <- ML asset config definition for feature engineering workflow
│       │
│       ├── ml-artifacts-asset.yml                  <- ML asset config definition for model and experiment
│       │
│       ├── monitoring-workflow-asset.yml           <- ML asset config definition for data monitoring workflow
{{ else -}}
│   ├── training                <- Folder for model development via MLflow recipes.
│   │   │
│   │   ├── steps               <- MLflow recipe steps (Python modules) implementing ML pipeline logic, e.g. model training and evaluation. Most
│   │   │                          development work happens here. See https://mlflow.org/docs/latest/recipes.html for details
│   │   │
│   │   ├── notebooks           <- Databricks notebook that runs the MLflow recipe, i.e. run the logic in `steps`. Used to
│   │   │                          drive code execution on Databricks for CI/CD. In most cases, you do not need to modify
│   │   │                          the notebook.
│   │   │
│   │   ├── recipe.yaml         <- The main recipe configuration file that declaratively defines the attributes and behavior
│   │   │                          of each recipe step, such as the input dataset to use for training a model or the
│   │   │                          performance criteria for promoting a model to production.
│   │   │
│   │   ├── profiles            <- Environment-specific (e.g. dev vs test vs prod) configurations for MLflow recipes execution.
│   │
│   │
│   ├── validation              <- Optional model validation step before deploying a model.
│   │
│   ├── monitoring              <- Model monitoring, feature monitoring, etc.
│   │
│   ├── deployment              <- Model deployment and endpoint deployment.
│   │   │
│   │   ├── batch_inference     <- Batch inference code that will run as part of scheduled workflow.
│   │   │
│   │   ├── model_deployment    <- As part of CD workflow, promote model to Production stage in model registry.
│   │
│   ├── tests                   <- Unit tests for the ML project, including modules under `steps`.
│   │
│   ├── assets               <- ML asset (ML jobs, MLflow models) config definitions expressed as code, across dev/staging/prod/test.
│       │
│       ├── model-workflow-asset.yml                <- ML asset config definition for model training, validation, deployment workflow
│       │
│       ├── batch-inference-workflow-asset.yml      <- ML asset config definition for batch inference workflow
│       │
│       ├── ml-artifacts-asset.yml                  <- ML asset config definition for model and experiment
│       │
│       ├── monitoring-workflow-asset.yml           <- ML asset config definition for data monitoring workflow
{{ end -}}
│
{{ if or (eq .input_cicd_platform `github_actions`) (eq .input_cicd_platform `github_actions_for_github_enterprise_servers`) -}}
├── .github                     <- Configuration folder for CI/CD using GitHub Actions. The CI/CD workflows deploy ML assets defined in the `./assets/*` folder with databricks CLI bundles.
{{ else if (eq .input_cicd_platform `azure_devops`) -}}
├── .azure                      <- Configuration folder for CI/CD using Azure DevOps Pipelines. The CI/CD workflows deploy ML assets defined in the `./assets/*` folder with databricks CLI bundles.
{{ end -}}
```

## Using this repo

The table below links to detailed docs explaining how to use this repo for different use cases.

This project comes with example ML code to train, validate and deploy a regression model to predict NYC taxi fares.
If you're a data scientist just getting started with this repo for a brand new ML project, we recommend 
adapting the provided example code to your ML problem. Then making and 
testing ML code changes on Databricks or your local machine. Follow the instructions from
the {{ if (eq .input_include_feature_store `yes`) }}[ML quickstart](docs/ml-developer-guide-fs.md).
{{ else }}[ML quickstart](docs/ml-developer-guide.md).{{ end }} 

When you're satisfied with initial ML experimentation (e.g. validated that a model with reasonable performance can be
trained on your dataset) and ready to deploy production training/inference
pipelines, ask your ops team to follow the [MLOps setup guide](docs/mlops-setup.md) to configure CI/CD and deploy 
production ML pipelines.

After that, follow the [ML pull request guide](docs/ml-pull-request.md)
and [ML asset config guide]({{template `project_name_alphanumeric_underscore` .}}/assets/README.md) to propose, test, and deploy changes to production ML code (e.g. update model parameters)
or pipeline assets (e.g. use a larger instance type for model training) via pull request.

| Role                          | Goal                                                                         | Docs                                                                                                                                                                |
|-------------------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Data Scientist                | Get started writing ML code for a brand new project                          | {{ if (eq .input_include_feature_store `yes`) }}[ML quickstart](docs/ml-developer-guide-fs.md).{{ else }}[ML quickstart](docs/ml-developer-guide.md){{ end }} |
| MLOps / DevOps                | Set up CI/CD for the current ML project   | [MLOps setup guide](docs/mlops-setup.md)                                                                                                                            |
| Data Scientist                | Update production ML code (e.g. model training logic) for an existing project | [ML pull request guide](docs/ml-pull-request.md)                                                                                                                    |
| Data Scientist                | Modify production model ML assets, e.g. model training or inference jobs  | [ML asset config guide]({{template `project_name_alphanumeric_underscore` .}}/assets/README.md)                                                     |

## Monorepo

It's possible to use the repo as a monorepo that contains multiple projects. All projects share the same workspaces and service principals.

For example, assuming there's existing repo with root directory name `monorepo_root_dir` and project name `project1`
1. Create another project from `databricks bundle init` with project name `project2` and root directory name `project2`.
2. Copy the internal directory `project2/project2` to root directory of existing repo `monorepo_root_dir/project2`.
{{ if or (eq .input_cicd_platform `github_actions`) (eq .input_cicd_platform `github_actions_for_github_enterprise_servers`) -}}
3. Copy yaml files from `project2/.github/workflows/` to `monorepo_root_dir/.github/workflows/` and make sure there's no name conflicts.
{{ end -}}
{{- if (eq .input_cicd_platform `azure_devops`) }}
3. Copy yaml files from `project2/.azure/devops-pipelines/` to `monorepo_root_dir/.azure/devops-pipelines/` and make sure there's no name conflicts.
{{ end -}}

