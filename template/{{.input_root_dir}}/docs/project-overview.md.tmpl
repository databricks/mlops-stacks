# Project Overview

[(back to main README)](../README.md)

## ML pipeline structure
This project defines an ML pipeline for automated retraining and batch inference of an ML model
on tabular data.

See the full pipeline structure below. The [MLOps Stacks README](https://github.com/databricks/mlops-stacks/blob/main/Pipeline.md)
contains additional details on how ML pipelines are tested and deployed across each of the dev, staging, prod environments below.

![MLOps Stacks diagram](images/mlops-stack-summary.png)


## Code structure
This project contains the following components:

| Component                  | Description                                                                                                                                                                                                                                                                                                                                             |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ML Code                    | Example ML project code, with unit tested Python modules and notebooks                                                                                                                                                                                                                                                                                  |
| ML Resource Config as Code | ML pipeline asset config (training and batch inference job schedules, etc) configured and deployed through [databricks CLI bundles]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/cli/bundle-cli.html")) }})                                                                                              |
| CI/CD                      | {{ if (eq .input_cicd_platform `github_actions`) }}[GitHub Actions](https://github.com/actions) workflows to test and deploy ML code and assets {{ else if (eq .input_cicd_platform `azure_devops`) }}[Azure DevOps Pipelines](https://azure.microsoft.com/en-gb/products/devops/pipelines/) to test and deploy ML code and assets{{ end }}      |

contained in the following files:

```
{{ template `root_dir` .}}        <- Root directory. Both monorepo and polyrepo are supported.
│
├── {{template `project_name_alphanumeric_underscore` .}}       <- Contains python code, notebooks and ML assets related to one ML project. 
│   │
│   ├── requirements.txt        <- Specifies Python dependencies for ML code (for example: model training, batch inference).
│   │
│   ├── databricks.yml          <- databricks.yml is the root ML asset config file for the ML project that can be loaded by databricks CLI bundles. It defines the bundle name, workspace URL and asset config component to be included.
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
│   │   ├── model_deployment    <- As part of CD workflow, promote model to Production stage in model registry.
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
│   │   ├── model_deployment    <- As part of CD workflow, promote model to Production stage in model registry.
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
├── .github                     <- Configuration folder for CI/CD using GitHub Actions. The CI/CD workflows run the notebooks
                                   under `notebooks` to test and deploy model training code
{{ else if (eq .input_cicd_platform `azure_devops`) -}}
├── .azure                      <- Configuration folder for CI/CD using Azure DevOps Pipelines. The CI/CD workflows run the notebooks
                                   under `notebooks` to test and deploy model training code
{{ end -}}
```

## Next Steps
See the [main README](../README.md#using-this-repo) for additional links on how to work with this repo.
