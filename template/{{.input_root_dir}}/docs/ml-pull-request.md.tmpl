# Updating ML code in production

[(back to main README)](../README.md)

**NOTE**: This page assumes that your MLOps team has already configured CI/CD and deployed initial
ML assets, per the [MLOps setup guide](mlops-setup.md).

## Table of contents
* [Intro](#intro)
* [Opening a pull request](#opening-a-pull-request)
* [Viewing test status and debug logs](#viewing-test-status-and-debug-logs)
* [Merging your pull request](#merging-your-pull-request)
* [Next steps](#next-steps)

## Intro
After following the
{{ if (eq .input_include_feature_store `yes`) }}[ML quickstart](ml-developer-guide-fs.md).
{{ else }}[ML quickstart](ml-developer-guide.md).{{ end }}
to iterate on ML code, the next step is to get
your updated code merged back into the repo for production use. This page walks you through the workflow
for doing so via a pull request.

## Opening a pull request

To push your updated ML code to production, [open a pull request]({{ if (eq .input_cicd_platform `github_actions`) }}https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
{{ else if (eq .input_cicd_platform `azure_devops`) }}https://learn.microsoft.com/en-us/azure/devops/repos/git/pull-requests?view=azure-devops&tabs=browser#create-a-pull-request
{{ end }}) against the remote Git repo containing the current project.

**NOTE**: the default tests provided in this repo require that you use a pull
request branch on the Git repo for the current project, rather than opening a pull request from a fork
of the Git repo. Support for running tests against pull requests from repo forks
is planned for the future.

## Viewing test status and debug logs
Opening a pull request will trigger a  
{{- if or (eq .input_cicd_platform `github_actions`) (eq .input_cicd_platform `github_actions_for_github_enterprise_servers`) -}} 
 [workflow](../.github/workflows/{{template `project_name` .}}-run-tests{{ if (eq .input_include_feature_store `yes`) }}-fs{{ end }}.yml)
{{- else if (eq .input_cicd_platform `azure_devops`) -}}
[Azure DevOps Pipeline](../.azure/devops-pipelines/{{template `project_name` .}}-tests-ci.yml)
{{ end }} 
that runs unit and integration tests for the{{ if (eq .input_include_feature_store `yes`) }} feature engineering and{{ end }} model training pipeline on Databricks against a test dataset.
You can view test status and debug logs from the pull request UI, and push new commits to your pull request branch
to address any test failures.
{{ if (eq .input_include_feature_store `yes`) }}
The integration test runs the feature engineering and model training notebooks as a multi-task Databricks Job in the staging workspace.
It reads input data, performs feature transforms, and writes outputs to Feature Store tables in the staging workspace. 
The model training notebook uses these Feature Store tables as inputs to train, validate and register a new model version in 
{{ if (eq .input_include_models_in_unity_catalog `no`) }} the workspace model registry
{{- else -}} UC
{{end}}. 
The fitted model along with its metrics and params will also be logged to an MLflow run. 
To debug failed integration test runs, click into the Databricks job run
URL printed in the test logs. The executed notebook of the job run will contain a link to the MLflow model training run, which you can use with the Experiments page in the workspace
to view training metrics or fetch and debug the model as needed.
{{- else }}
The integration test runs the model training notebook in the staging workspace, training, validating,
and registering a new model version in 
{{ if (eq .input_include_models_in_unity_catalog `no`) }} the workspace model registry
{{- else -}} UC
{{end}}.
The fitted model along with its metrics and params
will also be logged to an MLflow run. To debug failed integration test runs, click into the Databricks job run
URL printed in the test logs. The executed notebook of the job run will contain a link to the MLflow model training run. You can also use the Experiments page in the workspace
to view training metrics or fetch and debug the model as needed.
{{ end }}

## Merging your pull request
Once tests pass on your pull request, get your pull request reviewed and approved by a teammate,
and then merge it into the upstream repo.

## Next Steps
{{- if (eq .input_default_branch .input_release_branch) }}
After merging your pull request, subsequent runs of the {{ if (eq .input_include_feature_store `yes`) }}feature engineering,{{ end }} model training and batch inference
jobs in staging will automatically use your updated ML code.

You may want to wait to confirm that
the staging jobs succeed, then repeat the workflow above to open a pull request against the
`{{template `release_branch` .}}` branch to promote your ML code to production. Once your pull request against `{{template `release_branch` .}}`
merges, production jobs will also automatically include your changes. 

{{- else }}
After merging your pull request, subsequent runs of the model training and batch inference
jobs in staging and production will automatically use your updated ML code.
{{- end }}

You can track the state of the ML pipelines for the current project from the MLflow registered model UI. Links:
{{ if (eq .input_include_models_in_unity_catalog `no`) }}
* [Staging workspace registered model]({{template `databricks_staging_workspace_host` .}}/ml/models/staging-{{template `model_name` .}})
* [Prod workspace registered model]({{template `databricks_prod_workspace_host` .}}/ml/models/prod-{{template `model_name` .}})
{{- else -}} 
* [Staging model in UC]({{template `databricks_staging_workspace_host` .}}/explore/data/models/staging/{{template `project_name` .}}/{{template `model_name` .}})
* [Prod model in UC]({{template `databricks_prod_workspace_host` .}}/explore/data/models/prod/{{template `project_name` .}}/{{template `model_name` .}})
{{end}}. 

In both the staging and prod workspaces, the MLflow registered model contains links to:
* The model versions produced through automated retraining
* The Git repository containing the ML code run in the training and inference pipelines
 {{ if (eq .input_include_feature_store `yes`) }}* The recurring Feature Store jobs that computes and writes features to Feature Store tables. {{ end }}
* The recurring training job that produces new model versions using the latest ML code and data
* The model deployment CD workflow that takes model versions produced by the training job and deploys them for inference
* The recurring batch inference job that uses the currently-deployed model version to score a dataset
