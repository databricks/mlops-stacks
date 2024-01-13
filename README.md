# Databricks MLOps Stacks

> **_NOTE:_**  This feature is in [public preview](https://docs.databricks.com/release-notes/release-types.html).

This repo provides a customizable stack for starting new ML projects
on Databricks that follow production best-practices out of the box.

Using Databricks MLOps Stacks, data scientists can quickly get started iterating on ML code for new projects while ops engineers set up CI/CD and ML assets
management, with an easy transition to production. You can also use MLOps Stacks as a building block in automation for creating new data science projects with production-grade CI/CD pre-configured.

The default stack in this repo includes three modular components: 

| Component                   | Description                                                                                                                                                           | Why it's useful                                                                                                                                                                         |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [ML Code](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/)                     | Example ML project structure ([training](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/training) and [batch inference](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/deployment/batch_inference), etc), with unit tested Python modules and notebooks                                                                                           | Quickly iterate on ML problems, without worrying about refactoring your code into tested modules for productionization later on.                                                        |
| [ML Assets as Code](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/assets) | ML pipeline assets ([training](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/assets/model-workflow-asset.yml.tmpl) and [batch inference](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/assets/batch-inference-workflow-asset.yml.tmpl) jobs, etc) defined through [databricks CLI bundles](https://docs.databricks.com/dev-tools/cli/bundle-cli.html)    | Govern, audit, and deploy changes to your ML assets (e.g. "use a larger instance type for automated model retraining") through pull requests, rather than adhoc changes made via UI. |
| CI/CD([GitHub Actions](template/{{.input_root_dir}}/.github/) or [Azure DevOps](template/{{.input_root_dir}}/.azure/))                       | [GitHub Actions](https://docs.github.com/en/actions) or [Azure DevOps](https://azure.microsoft.com/en-us/products/devops) workflows to test and deploy ML code and assets | Ship ML code faster and with confidence: ensure all production changes are performed through automation and that only tested code is deployed to prod                                   |

See the [FAQ](#FAQ) for questions on common use cases.

## ML pipeline structure and development loops

An ML solution comprises data, code, and models. These assets need to be developed, validated (staging), and deployed (production). In this repository, we use the notion of dev, staging, and prod to represent the execution
environments of each stage. 

An instantiated project from MLOps Stacks contains an ML pipeline with CI/CD workflows to test and deploy automated model training and batch inference jobs across your dev, staging, and prod Databricks workspaces. 

<img src="doc-images/mlops-stack-summary.png">

Data scientists can iterate on ML code and file pull requests (PRs). This will trigger unit tests and integration tests in an isolated staging Databricks workspace. Model training and batch inference jobs in staging will immediately update to run the latest code when a PR is merged into main. After merging a PR into main, you can cut a new release branch as part of your regularly scheduled release process to promote ML code changes to production.

### Develop ML pipelines
https://github.com/databricks/mlops-stacks/assets/87999496/00eed790-70f4-4428-9f18-71771051f92a


### Create a PR and CI
https://github.com/databricks/mlops-stacks/assets/87999496/f5b3c82d-77a5-4ee5-85f5-8f00b026ae05


### Merge the PR and deploy to Staging
https://github.com/databricks/mlops-stacks/assets/87999496/7239e4d0-2327-4d30-91cc-5e7f8328ef73

https://github.com/databricks/mlops-stacks/assets/87999496/013c0d32-c283-494b-8c3f-2a9a60366207


### Deploy to Prod
https://github.com/databricks/mlops-stacks/assets/87999496/0d220d55-465e-4a69-bd83-1e66ad2e8464


[See this page](Pipeline.md) for detailed description and diagrams of the ML pipeline structure defined in the default stack. 

## Using MLOps Stacks

### Prerequisites
 - Python 3.8+
 - [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/databricks-cli.html) >= v0.211.0

[Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/databricks-cli.html) v0.211.0 contains [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) for the purpose of project creation.

Please follow [the instruction](https://docs.databricks.com/en/dev-tools/cli/databricks-cli-ref.html#install-the-cli) to install and set up databricks CLI. Releases of databricks CLI can be found in the [releases section](https://github.com/databricks/cli/releases) of databricks/cli repository.

[Databricks asset bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html) and [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) are in public preview.


### Start a new project

To create a new project, run:

    databricks bundle init mlops-stacks

This will prompt for parameters for project initialization. Some of these parameters are required to get started:
 * ``input_project_name``: name of the current project
 * ``input_root_dir``: name of the root directory. It is recommended to use the name of the current project as the root directory name, except in the case of a monorepo with other projects where the name of the monorepo should be used instead.
 * ``input_cloud``: Cloud provider you use with Databricks (AWS or Azure), note GCP is not supported at this time.
 * ``input_cicd_platform`` : CI/CD platform of choice (GitHub Actions or GitHub Actions for GitHub Enterprise Servers or Azure DevOps)

Others must be correctly specified for CI/CD to work, and so can be left at their default values until you're
ready to productionize a model. We recommend specifying any known parameters upfront (e.g. if you know
``input_databricks_staging_workspace_host``, it's better to specify it upfront):

 * ``input_databricks_staging_workspace_host``: URL of staging Databricks workspace, used to run CI tests on PRs and preview config changes before they're deployed to production.
   We encourage granting data scientists working on the current ML project non-admin (read) access to this workspace,
   to enable them to view and debug CI test results
 * ``input_databricks_prod_workspace_host``: URL of production Databricks workspace. We encourage granting data scientists working on the current ML project non-admin (read) access to this workspace,
   to enable them to view production job status and see job logs to debug failures.
 * ``input_default_branch``: Name of the default branch, where the prod and staging ML assets are deployed from and the latest ML code is staged.
 * ``input_release_branch``: Name of the release branch. The production jobs (model training, batch inference) defined in this
    repo pull ML code from this branch.
 * ``input_read_user_group``: User group name to give READ permissions to for project assets (ML jobs, integration test job runs, and machine learning assets). A group with this name must exist in both the staging and prod workspaces. Defaults to "users", which grants read permission to all users in the staging/prod workspaces. You can specify a custom group name e.g. to restrict read permissions to members of the team working on the current ML project.
  * ``input_include_models_in_unity_catalog``: If selected, models will be registered to [Unity Catalog](https://docs.databricks.com/en/mlflow/models-in-uc.html#models-in-unity-catalog). Models will be registered under a three-level namespace of `<catalog>.<schema_name>.<model_name>`, according the the target environment in which the model registration code is executed. Thus, if model registration code runs in the `prod` environment, the model will be registered to the `prod` catalog under the namespace `<prod>.<schema>.<model_name>`. This assumes that the respective catalogs exist in Unity Catalog (e.g. `dev`, `staging` and `prod` catalogs). Target environment names, and catalogs to be used are defined in the Databricks bundles files, and can be updated as needed.
 * ``input_schema_name``: If using [Models in Unity Catalog](https://docs.databricks.com/en/mlflow/models-in-uc.html#models-in-unity-catalog), specify the name of the schema under which the models should be registered, but we recommend keeping the name the same as the project name. We default to using the same `schema_name` across catalogs, thus this schema must exist in each catalog used. For example, the training pipeline when executed in the staging environment will register the model to `staging.<schema_name>.<model_name>`, whereas the same pipeline executed in the prod environment will register the mode to `prod.<schema_name>.<model_name>`. Also, be sure that the service principals in each respective environment have the right permissions to access this schema, which would be `USE_CATALOG`, `USE_SCHEMA`, `MODIFY`, `CREATE_MODEL`, and `CREATE_TABLE`.
 * ``input_unity_catalog_read_user_group``: If using [Models in Unity Catalog](https://docs.databricks.com/en/mlflow/models-in-uc.html#models-in-unity-catalog), define the name of the user group to grant `EXECUTE` (read & use model) privileges for the registered model. Defaults to "account users".
 * ``input_include_feature_store``: If selected, will provide [Databricks Feature Store](https://docs.databricks.com/machine-learning/feature-store/index.html) stack components including: project structure and sample feature Python modules, feature engineering notebooks, ML asset configs to provision and manage Feature Store jobs, and automated integration tests covering feature engineering and training.
 * ``input_include_mlflow_recipes``: If selected, will provide [MLflow Recipes](https://mlflow.org/docs/latest/recipes.html) stack components, dividing the training pipeline into configurable steps and profiles.

See the generated ``README.md`` for next steps!

## Customize MLOps Stacks
Your organization can use the default stack as is or customize it as needed, e.g. to add/remove components or
adapt individual components to fit your organization's best practices. See the
[stack customization guide](stack-customization.md) for more details.

## FAQ

### Do I need separate dev/staging/prod workspaces to use MLOps Stacks?
We recommend using separate dev/staging/prod Databricks workspaces for stronger
isolation between environments. For example, Databricks REST API rate limits
are applied per-workspace, so if using [Databricks Model Serving](https://docs.databricks.com/applications/mlflow/model-serving.html),
using separate workspaces can help prevent high load in staging from DOSing your
production model serving endpoints.

However, you can create a single workspace stack, by supplying the same workspace URL for
`input_databricks_staging_workspace_host` and `input_databricks_prod_workspace_host`. If you go this route, we
recommend using different service principals to manage staging vs prod assets,
to ensure that CI workloads run in staging cannot interfere with production assets.

### I have an existing ML project. Can I productionize it using MLOps Stacks?
Yes. Currently, you can instantiate a new project and copy relevant components
into your existing project to productionize it. MLOps Stacks is modularized, so
you can e.g. copy just the GitHub Actions workflows under `.github` or ML asset configs
 under ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/assets`` 
and ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/databricks.yml`` into your existing project.

### Can I adopt individual components of MLOps Stacks?
For this use case, we recommend instantiating via [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) 
and copying the relevant subdirectories. For example, all ML asset configs
are defined under ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/assets``
and ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/databricks.yml``, while CI/CD is defined e.g. under `.github`
if using GitHub Actions, or under `.azure` if using Azure DevOps.

### Can I customize my MLOps Stack?
Yes. We provide the default stack in this repo as a production-friendly starting point for MLOps.
However, in many cases you may need to customize the stack to match your organization's
best practices. See [the stack customization guide](stack-customization.md)
for details on how to do this.

### Does the MLOps Stacks cover data (ETL) pipelines?

Since MLOps Stacks is based on [databricks CLI bundles](https://docs.databricks.com/dev-tools/cli/bundle-commands.html),
it's not limited only to ML workflows and assets - it works for assets across the Databricks Lakehouse. For instance, while the existing ML
code samples contain feature engineering, training, model validation, deployment and batch inference workflows,
you can use it for Delta Live Tables pipelines as well.

### How can I provide feedback?

Please provide feedback (bug reports, feature requests, etc) via GitHub issues.

## Contributing

We welcome community contributions. For substantial changes, we ask that you first file a GitHub issue to facilitate
discussion, before opening a pull request.

MLOps Stacks is implemented as a [Databricks asset bundle template](https://docs.databricks.com/en/dev-tools/bundles/templates.html)
that generates new projects given user-supplied parameters. Parametrized project code can be found under
the `{{.input_root_dir}}` directory.

### Installing development requirements

To run tests, install [actionlint](https://github.com/rhysd/actionlint),
[databricks CLI](https://docs.databricks.com/dev-tools/cli/databricks-cli.html), [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm), and
[act](https://github.com/nektos/act), then install the Python
dependencies listed in `dev-requirements.txt`:

    pip install -r dev-requirements.txt

### Running the tests
**NOTE**: This section is for open-source developers contributing to the default stack
in this repo.  If you are working on an ML project using the stack (e.g. if you ran `databricks bundle init`
to start a new project), see the `README.md` within your generated
project directory for detailed instructions on how to make and test changes.

Run unit tests:

```
pytest tests
```

Run all tests (unit and slower integration tests):

```
pytest tests --large
```

Run integration tests only:

```
pytest tests --large-only
```

### Previewing changes
When making changes to MLOps Stacks, it can be convenient to see how those changes affect
a generated new ML project. To do this, you can create an example
project from your local checkout of the repo, and inspect its contents/run tests within
the project.

We provide example project configs for Azure (using both GitHub and Azure DevOps) and AWS (using GitHub) under `tests/example-project-configs`.
To create an example Azure project, using Azure DevOps as the CI/CD platform, run the following from the desired parent directory
of the example project:

```
# Note: update MLOPS_STACKS_PATH to the path to your local checkout of the MLOps Stacks repo
MLOPS_STACKS_PATH=~/mlops-stacks
databricks bundle init "$MLOPS_STACKS_PATH" --config-file "$MLOPS_STACKS_PATH/tests/example-project-configs/azure/azure-devops.json"
```

To create an example AWS project, using GitHub Actions for CI/CD, run:
```
# Note: update MLOPS_STACKS_PATH to the path to your local checkout of the MLOps Stacks repo
MLOPS_STACKS_PATH=~/mlops-stacks
databricks bundle init "$MLOPS_STACKS_PATH" --config-file "$MLOPS_STACKS_PATH/tests/example-project-configs/aws/aws-github.json"
```
