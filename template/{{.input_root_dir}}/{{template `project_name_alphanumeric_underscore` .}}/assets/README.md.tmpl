# Databricks ML Resource Configurations
[(back to main README)](../../README.md)

## Table of contents
* [Intro](#intro)
* [Local development and dev workspace](#local-development-and-dev-workspace)
* [CI/CD](#set-up-cicd)
* [Deploy initial ML assets](#deploy-initial-ml-assets)
* [Develop and test config changes](#develop-and-test-config-changes)
* [Deploy config changes](#deploy-config-changes)

## Intro

### databricks CLI bundles
MLOps Stacks ML assets are configured and deployed through [databricks CLI bundles]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/cli/bundle-cli.html")) }}).
The bundle setting file must be expressed in YAML format and must contain at minimum the top-level bundle mapping.

The databricks CLI bundles top level is defined by file `{{template `project_name_alphanumeric_underscore` .}}/databricks.yml`.
During databricks CLI bundles deployment, the root config file will be loaded, validated and deployed to workspace provided by the environment together with all the included assets.

ML Resource Configurations in this directory:
 - model workflow (`{{template `project_name_alphanumeric_underscore` .}}/assets/model-workflow-asset.yml`)
 - batch inference workflow (`{{template `project_name_alphanumeric_underscore` .}}/assets/batch-inference-workflow-asset.yml`)
 - monitoring workflow (`{{template `project_name_alphanumeric_underscore` .}}/assets/monitoring-workflow-asset.yml`)
 - feature engineering workflow (`{{template `project_name_alphanumeric_underscore` .}}/assets/feature-engineering-workflow-asset.yml`)
 - model definition and experiment definition (`{{template `project_name_alphanumeric_underscore` .}}/assets/ml-artifacts-asset.yml`)


### Deployment Config & CI/CD integration
The ML assets can be deployed to databricks workspace based on the databricks CLI bundles deployment config.
Deployment configs of different deployment targets share the general ML asset configurations with added ability to specify deployment target specific values (workspace URI, model name, jobs notebook parameters, etc).

This project ships with CI/CD workflows for developing and deploying ML asset configurations based on deployment config.

{{- if (eq .input_include_models_in_unity_catalog "yes") }}

NOTE: For Model Registry in Unity Catalog, we expect a catalog to exist with the name of the deployment target by default. For example, if the deployment target is `dev`, we expect a catalog named `dev` to exist in the workspace. 
If you want to use different catalog names, please update the `targets` declared in the `{{template `project_name_alphanumeric_underscore` .}}/databricks.yml` and `{{template `project_name_alphanumeric_underscore` .}}/assets/ml-artifacts-asset.yml` files.
If changing the `staging`, `prod`, or `test` deployment targets, you'll need to update the 
{{- if or (eq .input_cicd_platform `github_actions`) (eq .input_cicd_platform `github_actions_for_github_enterprise_servers`) }} workflows located in the `.github/workflows` directory.
{{- else if (eq .input_cicd_platform `azure_devops`) }}  pipelines located in the `azure-pipelines` directory.{{- end }}
{{- end }}


| Deployment Target | Description                                                                                                                                                                                                                           | Databricks Workspace | Model Name                          | Experiment Name                                |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|-------------------------------------|------------------------------------------------|
| dev         | The `dev` deployment target is used by ML engineers to deploy ML assets to development workspace with `dev` configs. The config is for ML project development purposes.                                                           | dev workspace        | dev-{{template `model_name` .}}     | /dev-{{template `experiment_base_name` .}}     |
| staging     | The `staging` deployment target is part of the CD pipeline. Latest {{template `default_branch` .}} content will be deployed to staging workspace with `staging` config.                                                             | staging workspace    | staging-{{template `model_name` .}} | /staging-{{template `experiment_base_name` .}} |
| prod        | The `prod` deployment target is part of the CD pipeline. Latest {{template `release_branch` .}} content will be deployed to prod workspace with `prod` config.                                                                      | prod workspace       | prod-{{template `model_name` .}}    | /prod-{{template `experiment_base_name` .}}    |
| test        | The `test` deployment target is part of the CI pipeline. For changes targeting the {{template `default_branch` .}} branch, upon making a PR, an integration test will be triggered and ML assets deployed to the staging workspace defined under `test` deployment target. | staging workspace    | test-{{template `model_name` .}}    | /test-{{template `experiment_base_name` .}}    |

During ML code development, you can deploy local ML asset configurations together with ML code to the a Databricks workspace to run the training, model validation or batch inference pipelines. The deployment will use `dev` config by default.

You can open a PR (pull request) to modify ML code or the asset config against {{template `default_branch` .}} branch.
The PR will trigger Python unit tests, followed by an integration test executed on the staging workspace, as defined under the `test` environment asset. 

Upon merging a PR to the {{template `default_branch` .}} branch, the {{template `default_branch` .}} branch content will be deployed to the staging workspace with `staging` environment asset configurations.

Upon merging code into the release branch, the release branch content will be deployed to prod workspace with `prod` environment asset configurations.


![ML asset config diagram](../../docs/images/mlops-stack-deploy.png)

## Local development and dev workspace

### Set up authentication

To set up the databricks CLI using a Databricks personal access token, take the following steps:

1. Follow [databricks CLI]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/cli/databricks-cli.html")) }}) to download and set up the databricks CLI locally.
2. Complete the `TODO` in `{{template `project_name_alphanumeric_underscore` .}}/databricks.yml` to add the dev workspace URI under `targets.dev.workspace.host`.
3. [Create a personal access token]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/auth.html#personal-access-tokens-for-users")) }})
  in your dev workspace and copy it.
4. Set an env variable `DATABRICKS_TOKEN` with your Databricks personal access token in your terminal. For example, run `export DATABRICKS_TOKEN=dapi12345` if the access token is dapi12345.
5. You can now use the databricks CLI to validate and deploy ML asset configurations to the dev workspace.

Alternatively, you can use the other approaches described in the [databricks CLI]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/cli/databricks-cli.html")) }}) documentation to set up authentication. For example, using your Databricks username/password, or seting up a local profile.

### Validate and provision ML asset configurations
1. After installing the databricks CLI and creating the `DATABRICKS_TOKEN` env variable, change to the `{{template `project_name_alphanumeric_underscore` .}}` directory.
2. Run `databricks bundle validate` to validate the Databricks asset configurations. 
3. Run `databricks bundle deploy` to provision the Databricks asset configurations to the dev workspace. The asset configurations and your ML code will be copied together to the dev workspace. The defined assets such as Databricks Workflows, MLflow Model and MLflow Experiment will be provisioned according to the config files under `{{template `project_name_alphanumeric_underscore` .}}/assets`.
4. Go to the Databricks dev workspace, check the defined model, experiment and workflows status, and interact with the created workflows.

### Destroy ML asset configurations
After development is done, you can run `databricks bundle destroy` to destroy (remove) the defined Databricks assets in the dev workspace. Any model version with `Production` or `Staging` stage will prevent the model from being deleted. Please update the version stage to `None` or `Archived` before destroying the ML assets.

## Set up CI/CD
Please refer to [mlops-setup](../../docs/mlops-setup.md#configure-cicd) for instructions to set up CI/CD.

## Deploy initial ML assets
After completing the prerequisites, create and push a PR branch adding all files to the Git repo:
```
git checkout -b add-ml-asset-config-and-code
git add .
git commit -m "Add ML asset config and ML code"
git push upstream add-ml-asset-config-and-code
```
Open a pull request to merge the pushed branch into the `{{template `default_branch` .}}` branch.
Upon creating this PR, the CI workflows will be triggered.
These CI workflow will run unit and integration tests of the ML code, 
in addition to validating the Databricks assets to be deployed to both staging and prod workspaces.
Once CI passes, merge the PR into the `{{template `default_branch` .}}` branch. This will deploy an initial set of Databricks assets to the staging workspace.
assets will be deployed to the prod workspace on pushing code to the `{{template `release_branch` .}}` branch.

Follow the next section to configure the input and output data tables for the batch inference job.

### Setting up the batch inference job
The batch inference job expects an input Delta table with a schema that your registered model accepts. To use the batch
inference job, set up such a Delta table in both your staging and prod workspaces.
Following this, update the batch_inference_job base parameters in `{{template `project_name_alphanumeric_underscore` .}}/assets/batch-inference-workflow-asset.yml` to pass
the name of the input Delta table and the name of the output Delta table to which to write batch predictions.

As the batch job will be run with the credentials of the service principal that provisioned it, make sure that the service
principal corresponding to a particular environment has permissions to read the input Delta table and modify the output Delta table in that environment's workspace. If the Delta table is in the [Unity Catalog](https://www.databricks.com/product/unity-catalog), these permissions are

* `USAGE` permissions for the catalog and schema of the input and output table.
* `SELECT` permission for the input table.
* `MODIFY` permission for the output table if it pre-dates your job.

### Setting up model validation
The model validation workflow focuses on building a plug-and-play stack component for continuous deployment (CD) of models 
in staging and prod.
Its central purpose is to evaluate a registered model and validate its quality before deploying the model to Production/Staging.

Model validation contains three components: 
* [model-workflow-asset.yml](./model-workflow-asset.yml) contains the asset config and input parameters for model validation.
* [validation.py](../validation/validation.py) defines custom metrics and validation thresholds that are referenced by the above asset config files.
* [notebooks/ModelValidation](../validation/notebooks/ModelValidation.py) contains the validation job implementation. In most cases you don't need to modify this file.

To set up and enable model validation, update [validation.py](../validation/validation.py) to return desired custom metrics and validation thresholds, then 
resolve the `TODOs` in the ModelValidation task of [model-workflow-asset.yml](./model-workflow-asset.yml).

## Develop and test config changes

### databricks CLI bundles schema overview
To get started, open `{{template `project_name_alphanumeric_underscore` .}}/assets/batch-inference-workflow-asset.yml`.  The file contains the ML asset definition of a batch inference job, like:

```$xslt
new_cluster: &new_cluster
  new_cluster:
    num_workers: 3
    spark_version: 13.3.x-cpu-ml-scala2.12
    node_type_id: {{template `cloud_specific_node_type_id` .}}
    custom_tags:
      clusterSource: mlops-stack/0.2

resources:
  jobs:
    batch_inference_job:
      name: ${bundle.target}-{{template `project_name` .}}-batch-inference-job
      tasks:
        - task_key: batch_inference_job
          <<: *new_cluster
          notebook_task:
            notebook_path: ../deployment/batch_inference/notebooks/BatchInference.py
            base_parameters:
              env: ${bundle.target}
              input_table_name: batch_inference_input_table_name
              ...
```

The example above defines a Databricks job with name `${bundle.target}-{{template `project_name` .}}-batch-inference-job`
that runs the notebook under `{{template `project_name_alphanumeric_underscore` .}}/deployment/batch_inference/notebooks/BatchInference.py` to regularly apply your ML model for batch inference. 

At the start of the asset definition, we declared an anchor `new_cluster` that will be referenced and used later. For more information about anchors in yaml schema, please refer to the [yaml documentation](https://yaml.org/spec/1.2.2/#3222-anchors-and-aliases).

We specify a `batch_inference_job` under `assets/jobs` to define a databricks workflow with internal key `batch_inference_job` and job name `{bundle.target}-{{template `project_name` .}}-batch-inference-job`.
The workflow contains a single task with task key `batch_inference_job`. The task runs notebook `../deployment/batch_inference/notebooks/BatchInference.py` with provided parameters `env` and `input_table_name` passing to the notebook.
After setting up databricks CLI, you can run command `databricks bundle schema`  to learn more about databricks CLI bundles schema.

The notebook_path is the relative path starting from the asset yaml file.

### Environment config based variables
The `${bundle.target}` will be replaced by the environment config name during the bundle deployment. For example, during the deployment of a `test` environment config, the job name will be
`test-{{template `project_name` .}}-batch-inference-job`. During the deployment of the `staging` environment config, the job name will be
`staging-{{template `project_name` .}}-batch-inference-job`.


To use different values based on different environment, you can use bundle variables based on the given target, for example,
```$xslt
variables:
  batch_inference_input_table: 
    description: The table name to be used for input to the batch inference workflow.
    default: input_table

targets:
  dev:
    variables:
      batch_inference_input_table: dev_table
  test:
    variables:
      batch_inference_input_table: test_table

new_cluster: &new_cluster
  new_cluster:
    num_workers: 3
    spark_version: 13.3.x-cpu-ml-scala2.12
    node_type_id: {{template `cloud_specific_node_type_id` .}}
    custom_tags:
      clusterSource: mlops-stack/0.2

resources:
  jobs:
    batch_inference_job:
      name: ${bundle.target}-{{template `project_name` .}}-batch-inference-job
      tasks:
        - task_key: batch_inference_job
          <<: *new_cluster
          notebook_task:
            notebook_path: ../deployment/batch_inference/notebooks/BatchInference.py
            base_parameters:
              env: ${bundle.target}
              input_table_name: ${var.batch_inference_input_table}
              ...
```
The `batch_inference_job` notebook parameter `input_table_name` is using a bundle variable `batch_inference_input_table` with default value "input_table".
The variable value will be overwritten with "dev_table" for `dev` environment config and "test_table" for `test` environment config:
- during deployment with the `dev` environment config, the `input_table_name` parameter will get the value "dev_table"
- during deployment with the `staging` environment config, the `input_table_name` parameter will get the value "input_table"
- during deployment with the `prod` environment config, the `input_table_name` parameter will get the value "input_table"
- during deployment with the `test` environment config, the `input_table_name` parameter will get the value "test_table"

### Test config changes
To test out a config change, simply edit one of the fields above. For example, increase the cluster size by updating `num_workers` from 3 to 4. 

Then follow [Local development and dev workspace](#local-development-and-dev-workspace) to deploy the change to the dev workspace.
Alternatively you can open a PR. Continuous integration will then validate the updated config and deploy tests to the to staging workspace.

## Deploy config changes

### Dev workspace deployment
Please refer to [Local development and dev workspace](#local-development-and-dev-workspace).

### Test workspace deployment(CI)
After setting up CI/CD, PRs against the {{template `default_branch` .}} branch will trigger CI workflows to run unit tests, integration test and asset validation.
The integration test will deploy MLflow model, MLflow experiment and Databricks workflow assets defined under the `test` environment asset config to the staging workspace. The integration test then triggers a run of the model workflow to verify the ML code. 

### Staging and Prod workspace deployment(CD)
After merging a PR to the {{template `default_branch` .}} branch, continuous deployment automation will deploy the `staging` assets to the staging workspace.

When you about to cut a release, you can create and merge a PR to merge changes from {{template `default_branch` .}} to {{template `release_branch` .}}. Continuous deployment automation will deploy `prod` assets to the prod workspace.

[Back to main project README](../../README.md)
