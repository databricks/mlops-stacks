# Databricks AgentOps Stacks

> **_NOTE:_**  This feature is in [public preview](https://docs.databricks.com/release-notes/release-types.html).

This repo provides a customizable stack for starting new AI Agent projects
on Databricks that follow production best-practices out of the box.

Using Databricks AgentOps Stacks, data scientists can quickly get started iterating on agent code for new projects while ops engineers set up CI/CD and resources
management, with an easy transition to production. You can also use AgentOps Stacks as a building block in automation for creating new data science projects with production-grade CI/CD pre-configured.

The default stack in this repo includes three modular components: 

| Component                   | Description                                                                                                                                                           | Why it's useful                                                                                                                                                                         |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Agent Code](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/)                     | Example Agent project structure ([data preparation](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/data_preparation) and [agent development](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/deployment/agent_development), etc), with unit tested Python modules and notebooks                                                                                           | Quickly iterate on Agent problems, without worrying about refactoring your code into tested modules for productionization later on.                                                        |
| [Agent Resources as Code](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/resources) | Agent pipeline resources ([data preparation](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/resources/data-preparation-resource.yml.tmpl) and [agent development](template/{{.input_root_dir}}/{{template%20`project_name_alphanumeric_underscore`%20.}}/resources/agent_resource.yml.tmpl) jobs, etc) defined through [Databricks CLI bundles](https://docs.databricks.com/dev-tools/cli/bundle-cli.html)    | Govern, audit, and deploy changes to your Agent resources (e.g. "use a larger instance type for automated model retraining") through pull requests, rather than adhoc changes made via UI. |
| CI/CD ([GitHub Actions](template/{{.input_root_dir}}/.github/) or [Azure DevOps](template/{{.input_root_dir}}/.azure/))                       | [GitHub Actions](https://docs.github.com/en/actions) or [Azure DevOps](https://azure.microsoft.com/en-us/products/devops) workflows to test and deploy code and resources | Ship code faster and with confidence: ensure all production changes are performed through automation and that only tested code is deployed to prod                                   |

See the [FAQ](#FAQ) for questions on common use cases.

## Agent pipeline structure and development loops

An Agent solution comprises data, code, and models. These resources need to be developed, validated (staging), and deployed (production). In this repository, we use the notion of dev, staging, and prod to represent the execution
environments of each stage. 

An instantiated project from AI Agent Ops Stacks contains an Agent pipeline with CI/CD workflows to test and deploy automated data preparation and agent development jobs across your dev, staging, and prod Databricks workspaces. 

Data scientists can iterate on Agent code and file pull requests (PRs). This will trigger unit tests and integration tests in an isolated staging Databricks workspace. Data preparation and agent development jobs in staging will immediately update to run the latest code when a PR is merged into main. After merging a PR into main, you can cut a new release branch as part of your regularly scheduled release process to promote Agent code changes to production.

## Using AI Agent Ops Stacks

### Prerequisites
 - Python 3.8+
 - [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/databricks-cli.html) >= v0.256.0

[Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/databricks-cli.html) contains [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) for the purpose of project creation.

Please follow [the instruction](https://docs.databricks.com/en/dev-tools/cli/databricks-cli-ref.html#install-the-cli) to install and set up Databricks CLI. Releases of Databricks CLI can be found in the [releases section](https://github.com/databricks/cli/releases) of Databricks/cli repository.

[Databricks asset bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html) and [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) are in public preview.


### Start a new project

To create a new project, run:

    databricks bundle init agentops-stacks

This will prompt for parameters for initialization. Some of these parameters are required to get started:
 * ``input_setup_cicd_and_project`` : If both CI/CD and the project should be set up, or only one of them. 
   * ``CICD_and_Project`` - Setup both CI/CD and project, the default option.
   * ``Project_Only`` - Setup project only, easiest for Data Scientists to get started with.
   * ``CICD_Only`` - Setup CI/CD only, likely for monorepo setups or setting up CI/CD on an already initialized project.
   We expect Data Scientists to specify ``Project_Only`` to get 
   started in a development capacity, and when ready to move the project to Staging/Production, CI/CD can be set up. We expect that step to be done by Machine Learning Engineers (MLEs) who can specify ``CICD_Only`` during initialization and use the provided workflow to setup CI/CD for one or more projects.
 * ``input_root_dir``: name of the root directory. When initializing with ``CICD_and_Project``, this field will automatically be set to ``input_project_name``.
 * ``input_cloud``: Cloud provider you use with Databricks (AWS, Azure, or GCP).

Others must be correctly specified for CI/CD to work:
 * ``input_cicd_platform`` : CI/CD platform of choice. Currently we support GitHub Actions, GitHub Actions for GitHub Enterprise Servers, Azure DevOps and GitLab.
 * ``input_databricks_staging_workspace_host``: URL of staging Databricks workspace, used to preview config changes before they're deployed to production. We encourage granting data scientists working on the current ML project non-admin (read) access to this workspace,
   to enable them to view and debug CI test results
 * ``input_databricks_prod_workspace_host``: URL of production Databricks workspace. We encourage granting data scientists working on the current ML project non-admin (read) access to this workspace,
   to enable them to view production job status and see job logs to debug failures.
 * ``input_default_branch``: Name of the default branch, where the prod and staging resources are deployed from and the latest code is staged.
 * ``input_release_branch``: Name of the release branch. The production jobs (model training, batch inference) defined in this
    repo pull code from this branch.

Or used for project initialization:
 * ``input_project_name``: name of the current project
 * ``input_read_user_group``: User group name to give READ permissions to for project resources (ML jobs, integration test job runs, and machine learning resources). A group with this name must exist in both the staging and prod workspaces. Defaults to "users", which grants read permission to all users in the staging/prod workspaces. You can specify a custom group name e.g. to restrict read permissions to members of the team working on the current ML project.
 * ``input_schema_name``: To store [Models in Unity Catalog](https://docs.databricks.com/en/mlflow/models-in-uc.html#models-in-unity-catalog), specify the name of the schema under which the models should be registered, but we recommend keeping the name the same as the project name. We default to using the same `schema_name` across catalogs, thus this schema must exist in each catalog used. For example, the training pipeline when executed in the staging environment will register the model to `staging.<schema_name>.<model_name>`, whereas the same pipeline executed in the prod environment will register the mode to `prod.<schema_name>.<model_name>`. Also, be sure that the service principals in each respective environment have the right permissions to access this schema, which would be `USE_CATALOG`, `USE_SCHEMA`, `MODIFY`, `CREATE_MODEL`, and `CREATE_TABLE`.
 * ``input_unity_catalog_read_user_group``: If using [Models in Unity Catalog](https://docs.databricks.com/en/mlflow/models-in-uc.html#models-in-unity-catalog), define the name of the user group to grant `EXECUTE` (read & use model) privileges for the registered model. Defaults to "account users".

See the generated ``README.md`` for next steps!

## Customize AgentOps Stacks
Your organization can use the default stack as is or customize it as needed, e.g. to add/remove components or
adapt individual components to fit your organization's best practices. See the
[stack customization guide](stack-customization.md) for more details.

## FAQ

### Do I need separate dev/staging/prod workspaces to use AgentOps Stacks?
We recommend using separate dev/staging/prod Databricks workspaces for stronger
isolation between environments. For example, Databricks REST API rate limits
are applied per-workspace, so if using [Databricks Model Serving](https://docs.databricks.com/applications/mlflow/model-serving.html),
using separate workspaces can help prevent high load in staging from DOSing your
production model serving endpoints.

However, you can create a single workspace stack, by supplying the same workspace URL for
`input_databricks_staging_workspace_host` and `input_databricks_prod_workspace_host`.
If you go this route, we
recommend using different service principals to manage staging vs prod resources,
to ensure that CI workloads run in staging cannot interfere with production resources.

### I have an existing Agent project. Can I productionize it using AI Agent Ops Stacks?
Yes. Currently, you can instantiate a new project and copy relevant components
into your existing project to productionize it. AgentOps Stacks is modularized, so
you can e.g. copy just the GitHub Actions workflows under `.github` or ML resource configs
 under ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/resources`` 
and ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/databricks.yml`` into your existing project.

### Can I adopt individual components of AI Agent Ops Stacks?
For this use case, we recommend instantiating via [Databricks asset bundle templates](https://docs.databricks.com/en/dev-tools/bundles/templates.html) 
and copying the relevant subdirectories. For example, all agent resource configs
are defined under ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/resources``
and ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/databricks.yml``, while CI/CD is defined e.g. under `.github`
if using GitHub Actions, or under `.azure` if using Azure DevOps.

### Can I customize my Agent Ops Stack?
Yes. We provide the default stack in this repo as a production-friendly starting point for AgentOps.
However, in many cases you may need to customize the stack to match your organization's
best practices. See [the stack customization guide](stack-customization.md)
for details on how to do this.

### Does the AgentOps Stacks cover data (ETL) pipelines?

Since AgentOps Stacks is based on [Databricks CLI bundles](https://docs.databricks.com/dev-tools/cli/bundle-commands.html),
it's not limited only to Agent workflows and resources - it works for resources across the Databricks Lakehouse. For instance, while the existing Agent code samples contain data ingestion, agent development, and agent deployment workflows, you can use it for Delta Live Tables pipelines as well.

### How can I provide feedback?

Please provide feedback (bug reports, feature requests, etc) via GitHub issues.

## Contributing

We welcome community contributions. For substantial changes, we ask that you first file a GitHub issue to facilitate
discussion, before opening a pull request.

AgentOps Stacks is implemented as a [Databricks asset bundle template](https://docs.databricks.com/en/dev-tools/bundles/templates.html)
that generates new projects given user-supplied parameters. Parametrized project code can be found under
the `{{.input_root_dir}}` directory.

### Installing development requirements

To run tests, install [actionlint](https://github.com/rhysd/actionlint),
[Databricks CLI](https://docs.databricks.com/dev-tools/cli/databricks-cli.html), [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm), and
[act](https://github.com/nektos/act), then install the Python
dependencies listed in `dev-requirements.txt`:

    pip install -r dev-requirements.txt

### Running the tests
**NOTE**: This section is for open-source developers contributing to the default stack
in this repo.  If you are working on an Agent project using the stack (e.g. if you ran `databricks bundle init`
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
