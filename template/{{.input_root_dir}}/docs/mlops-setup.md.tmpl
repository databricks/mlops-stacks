# MLOps Setup Guide
[(back to main README)](../README.md)

## Table of contents
* [Intro](#intro)
* [Create a hosted Git repo](#create-a-hosted-git-repo)
* [Configure CI/CD]({{ if (eq .input_cicd_platform `github_actions`) }}#configure-cicd---github-actions{{ else if (eq .input_cicd_platform `azure_devops`) }}#configure-cicd---azure-devops{{ end }})
{{- if (eq .input_include_mlflow_recipes `yes`) }}
* [Configure profiles for tests, staging, and prod](#configure-profiles-for-tests-staging-and-prod){{ end }}
* [Merge PR with initial ML code](#merge-a-pr-with-your-initial-ml-code)
{{ if not (eq .input_release_branch .input_default_branch) -}}
* [Create release branch](#create-release-branch)
{{ end -}}
* [Deploy ML assets and enable production jobs](#deploy-ml-assets-and-enable-production-jobs)
* [Next steps](#next-steps)

## Intro
This page explains how to productionize the current project, setting up CI/CD and
ML asset deployment, and deploying ML training and inference jobs.

After following this guide, data scientists can follow the [ML Pull Request](ml-pull-request.md) and
[ML Config](../{{template `project_name_alphanumeric_underscore` .}}/assets/README.md)  guides to make changes to ML code or deployed jobs.

## Create a hosted Git repo
Create a hosted Git repo to store project code, if you haven't already done so. From within the project
directory, initialize Git and add your hosted Git repo as a remote:
```
git init --initial-branch={{template `default_branch` .}}
```

```
git remote add upstream <hosted-git-repo-url>
```

Commit the current `README.md` file and other docs to the `{{template `default_branch` .}}` branch of the repo, to enable forking the repo:
```
git add README.md docs .gitignore {{template `project_name_alphanumeric_underscore` .}}/assets/README.md
git commit -m "Adding project README"
git push upstream {{template `default_branch` .}}
```

{{ if (eq .input_cicd_platform `github_actions`) -}}
## Configure CI/CD - GitHub Actions

### Prerequisites
* You must be an account admin to add service principals to the account.
* You must be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console]({{template `databricks_staging_workspace_host` .}}#setting/accounts) and
  [prod workspace admin console]({{template `databricks_prod_workspace_host` .}}#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.

### Set up authentication for CI/CD
#### Set up Service Principal
{{ if eq .input_cloud `azure` }}
To authenticate and manage ML assets created by CI/CD, 
[service principals]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals")) }})
for the project should be created and added to both staging and prod workspaces. Follow
[Add a service principal to your Azure Databricks account]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals#--add-a-service-principal-to-your-azure-databricks-account")) }})
and [Add a service principal to a workspace]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals#--add-a-service-principal-to-a-workspace")) }})
for details.

For your convenience, we also have Terraform modules that can be used to [create](https://registry.terraform.io/modules/databricks/mlops-azure-project-with-sp-creation/databricks/latest) or [link](https://registry.terraform.io/modules/databricks/mlops-azure-project-with-sp-linking/databricks/latest) service principals.

{{ else if eq .input_cloud `aws` }}
To authenticate and manage ML assets created by CI/CD, 
[service principals]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html")) }})
for the project should be created and added to both staging and prod workspaces. Follow
[Add a service principal to your Databricks account]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html#add-a-service-principal-to-your-databricks-account")) }})
and [Add a service principal to a workspace]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html#add-a-service-principal-to-a-workspace")) }})
for details.

For your convenience, we also have a [Terraform module](https://registry.terraform.io/modules/databricks/mlops-aws-project/databricks/latest) that can set up your service principals.
{{ end }}

#### Configure Service Principal (SP) permissions 
If the created project uses **Unity Catalog**, we expect a catalog to exist with the name of the deployment target by default. 
For example, if the deployment target is dev, we expect a catalog named dev to exist in the workspace. 
If you want to use different catalog names, please update the targets declared in the [{{template `project_name` .}}/databricks.yml](../{{template `project_name_alphanumeric_underscore` .}}/databricks.yml)
and [{{template `project_name` .}}/assets/ml-artifacts-asset.yml](../{{template `project_name_alphanumeric_underscore` .}}/assets/ml-artifacts-asset.yml)
 files. 
If changing the staging, prod, or test deployment targets, you'll need to update the workflows located in the .github/workflows directory.

The SP must have proper permission in each respective environment and the catalog for the environments.

For the integration test and the ML training job, the SP must have permissions to read the input Delta table and create experiment and models. 
i.e. for each environment:
- USE_CATALOG
- USE_SCHEMA
- MODIFY
- CREATE_MODEL
- CREATE_TABLE

For the batch inference job, the SP must have permissions to read input Delta table and modify the output Delta table. 
i.e. for each environment
- USAGE permissions for the catalog and schema of the input and output table.
- SELECT permission for the input table.
- MODIFY permission for the output table if it pre-dates your job.


#### Set secrets for CI/CD
{{ if and (eq .input_cicd_platform `github_actions`) (eq .input_cloud `aws`) }}
After creating the service principals and adding them to the respective staging and prod workspaces, follow
[Manage access tokens for a service principal]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html#manage-access-tokens-for-a-service-principal")) }})
to get service principal tokens for staging and prod workspace and follow [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
to add the secrets to GitHub:
- `STAGING_WORKSPACE_TOKEN` : service principal token for staging workspace
- `PROD_WORKSPACE_TOKEN` : service principal token for prod workspace
Be sure to update the [Workflow Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token) section under Repo Settings > Actions > General to allow `Read and write permissions`.
  {{ end }}

{{ if and (eq .input_cicd_platform `github_actions`) (eq .input_cloud `azure`) }}
After creating the service principals and adding them to the respective staging and prod workspaces, refer to
[Manage access tokens for a service principal]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals#--manage-access-tokens-for-a-service-principal")) }})
and [Get Azure AD tokens for service principals]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/api/latest/aad/service-prin-aad-token")) }})
to get your service principal credentials (tenant id, application id, and client secret) for both the staging and prod service principals, and [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
to add the following secrets to GitHub:
- `PROD_AZURE_SP_TENANT_ID`
- `PROD_AZURE_SP_APPLICATION_ID`
- `PROD_AZURE_SP_CLIENT_SECRET`
- `STAGING_AZURE_SP_TENANT_ID`
- `STAGING_AZURE_SP_APPLICATION_ID`
- `STAGING_AZURE_SP_CLIENT_SECRET`
Be sure to update the [Workflow Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token) section under Repo Settings > Actions > General to allow `Read and write permissions`.
  {{ end }}

{{ else if (eq .input_cicd_platform `azure_devops`) -}}
## Configure CI/CD - Azure DevOps

Two Azure DevOps Pipelines are defined under `.azure/devops-pipelines`:

- **`{{template `project_name` .}}-tests-ci.yml`**:<br>
  - **[CI]** Performs unit and integration tests<br>
    - Triggered on PR to main
- **`{{template `project_name` .}}-bundle-cicd.yml`**:<br>
  - **[CI]** Performs validation of Databricks assets defined under `{{template `project_name_alphanumeric_underscore` .}}/assets`<br>
    - Triggered on PR to main<br>
  - **[CD]** Deploys Databricks assets to the staging workspace<br>
    - Triggered on merging into main<br>
  - **[CD]** Deploys Databricks assets to the prod workspace<br>
    - Triggered on merging into release

> Note that these workflows are provided as example CI/CD workflows, and can be easily modified to match your preferred CI/CD order of operations.

Within the CI/CD pipelines defined under `.azure/devops-pipelines`, we will be deploying Databricks assets to the defined staging and prod workspaces using the `databricks` CLI. This requires setting up authentication between the `databricks` CLI and Databricks. By default we show how to authenticate with service principals by passing [secret variables from a variable group](https://learn.microsoft.com/en-us/azure/devops/pipelines/scripts/cli/pipeline-variable-group-secret-nonsecret-variables?view=azure-devops). In a production setting it is recommended to either use an [Azure Key Vault](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault?view=azure-devops&tabs=yaml) to store these secrets, or alternatively use [Azure service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml). We describe below how you can adapt the project Pipelines to leverage service connections. Let's add these.

```
git add .azure/devops-pipelines/{{template `project_name` .}}-bundle-cicd.yml .azure/devops-pipelines/{{template `project_name` .}}-tests-ci.yml 
git commit -m "Adding devops-pipeline files"
git push upstream {{template `default_branch` .}}
```

### Service principal approach [Default]

By default, we provide Azure Pipelines where authentication is done using service principals.

#### Requirements:
- You must be an account admin to add service principals to the account.
- You must be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console]({{template `databricks_staging_workspace_host` .}}#setting/accounts) and
  [prod workspace admin console]({{template `databricks_prod_workspace_host` .}}#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.
- Permissions to create Azure DevOps Pipelines in your Azure DevOps project. See the following [Azure DevOps prerequisites](https://learn.microsoft.com/en-us/azure/devops/organizations/security/about-permissions).
- Permissions to create Azure DevOps build policies. See the following [prerequisites](https://learn.microsoft.com/azure/devops/repos/git/branch-policies).

#### Steps:
{{ if (eq .input_cloud `azure`) }}
1. Create two service principals - one to be used for deploying and running staging assets, and one to be used for deploying and running production assets. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals")) }}) for details on how to create a service principal.
1. [Add the staging and production service principals to your Azure Databricks account]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals#add-service-principals-to-your-account-using-the-account-console")) }}), and following this add the staging service principal to the staging workspace, and production service principal to the production workspace. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html")) }}) for details.
1. Follow ['Get Azure AD tokens for the service principals']({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "dev-tools/api/latest/aad/service-prin-aad-token")) }})
to get your service principal credentials (tenant id, application id, and client secret) for both the staging and prod service principals. You will use these credentials as variables in the project Azure Pipelines.
1. Create two separate Azure Pipelines under your Azure DevOps project using the ‘Existing Azure Pipelines YAML file’ option. One of these pipelines will use the `{{template `project_name` .}}-tests-ci.yml` script, and the other will use the `{{template `project_name` .}}-bundles-cicd.yml` script. See [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline) for more details on creating Azure Pipelines.
1. Create a new variable group called `{{template `project_name` .}} variable group` defining the following secret variables, for more details [here](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic#create-a-variable-group):
    - `PROD_AZURE_SP_TENANT_ID`: tenant ID for the prod service principal
    - `PROD_AZURE_SP_APPLICATION_ID`: application (client) ID for the prod service principal
    - `PROD_AZURE_SP_CLIENT_SECRET`: client secret for the prod service principal
    - `STAGING_AZURE_SP_TENANT_ID`: tenant ID for the staging service principal
    - `STAGING_AZURE_SP_APPLICATION_ID`: application (client) ID for the staging service principal
    - `STAGING_AZURE_SP_CLIENT_SECRET`: client secret for the prod service principal
  {{ end }}
{{ if (eq .input_cloud `aws`) }}
1. Create two service principals - one to be used for deploying and running staging assets, and one to be used for deploying and running production assets. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html")) }}) for details on how to create a service principal.
1. [Add the staging and production service principals to your Databricks account]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html#add-service-principals-to-your-account-using-the-account-console")) }}), and following this add the staging service principal to the staging workspace, and production service principal to the production workspace. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html")) }}) for details.
1. Follow ['Get tokens for the service principals']({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html#manage-personal-access-tokens-for-a-service-principal")) }})
to get your service principal token for both the staging and prod service principals. You will use the token as variables in the project Azure Pipelines.
1. Create two separate Azure Pipelines under your Azure DevOps project using the ‘Existing Azure Pipelines YAML file’ option. One of these pipelines will use the `{{template `project_name` .}}-tests-ci.yml` script, and the other will use the `{{template `project_name` .}}-bundles-cicd.yml` script. See [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline) for more details on creating Azure Pipelines.
1. Create a new variable group called `{{template `project_name` .}} variable group` defining the following secret variables, for more details [here](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic#create-a-variable-group):
    - `STAGING_WORKSPACE_TOKEN` : service principal token for staging workspace
    - `PROD_WORKSPACE_TOKEN` : service principal token for prod workspace
  {{ end }}
      - Ensure that the two Azure Pipelines created in the prior step have access to these variables by selecting the name of the pipelines under the 'Pipeline permissions' tab of this variable group.
      - Alternatively you could store these secrets in an [Azure Key Vault](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/key-vault-in-own-project?view=azure-devops&tabs=portal) and link those secrets as variables to be used in the Pipelines.
1. Define two [build validation branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser#build-validation) for the `{{template `default_branch` .}}` branch using the two Azure build pipelines created in step 1. This is required so that any PR changes to the `{{template `default_branch` .}}` must build successfully before PRs can complete.

{{ if (eq .input_cloud `azure`) }}
### Service connection approach [Recommended in production settings]

#### Requirements:
- You must be an Azure account admin to add service principals to the account.
- You must be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console]({{template `databricks_staging_workspace_host` .}}#setting/accounts) and
  [prod workspace admin console]({{template `databricks_prod_workspace_host` .}}#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.
- Permissions to create service connections within an Azure subscription. See the following [prerequisites](https://docs.microsoft.com/azure/devops/pipelines/library/service-endpoints).
- Permissions to create Azure DevOps Pipelines in your Azure DevOps project. See the following [Azure DevOps prerequisites](https://learn.microsoft.com/en-us/azure/devops/organizations/security/about-permissions).
- Permissions to create Azure DevOps build policies. See the following [prerequisites](https://learn.microsoft.com/azure/devops/repos/git/branch-policies).

The ultimate aim of the service connection approach is to use two separate service connections, authenticated with a staging service principal and a production service principal, to deploy and run assets in the respective Azure Databricks workspaces. Taking this approach then negates the need to read client secrets or client IDs from the CI/CD pipelines.

#### Steps:
1. Create two service principals - one to be used for deploying and running staging assets, and one to be used for deploying and running production assets. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals")) }}) for details on how to create a service principal.
1. [Add the staging and production service principals to your Azure Databricks account]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals#add-service-principals-to-your-account-using-the-account-console")) }}), and following this add the staging service principal to the staging workspace, and production service principal to the production workspace. See [here]({{ template `generate_doc_link` (map (pair "cloud" .input_cloud) (pair "path" "administration-guide/users-groups/service-principals.html")) }}) for details.
1. [Create two Azure Resource Manager service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml#create-a-service-connection) - one to be used to deploy to staging Databricks assets, the other for production assets. Each of these service connections should be authenticated with the respective staging and production service principals created in the prior step.
1. Update both pipeline YAML files to use service connections rather than pipeline variables:
   - First, remove any lines where the environment variables are set in tasks in `{{template `project_name` .}}-tests-ci.yml` or `{{template `project_name` .}}-bundle-cicd.yml` files. Specifically, any lines where the following env vars are used: `PROD_AZURE_SP_TENANT_ID`, `PROD_AZURE_SP_APPLICATION_ID`, `PROD_AZURE_SP_CLIENT_SECRET`, `STAGING_AZURE_SP_TENANT_ID`, `STAGING_AZURE_SP_APPLICATION_ID`, `STAGING_AZURE_SP_CLIENT_SECRET`
   - Then, add the following AzureCLI task prior to installing the `databricks` cli in any of the pipeline jobs:

```yaml
# Get Azure Resource Manager variables using service connection
- task: AzureCLI@2
  displayName: 'Extract information from Azure CLI'
  inputs:
    azureSubscription: # TODO: insert SERVICE_CONNECTION_NAME
    addSpnToEnvironment: true
    scriptType: bash
    scriptLocation: inlineScript
    inlineScript: |
      subscription_id=$(az account list --query "[?isDefault].id"|jq -r '.[0]')
      echo "##vso[task.setvariable variable=ARM_CLIENT_ID]${servicePrincipalId}"
      echo "##vso[task.setvariable variable=ARM_CLIENT_SECRET;issecret=true]${servicePrincipalKey}"
      echo "##vso[task.setvariable variable=ARM_TENANT_ID]${tenantId}"
      echo "##vso[task.setvariable variable=ARM_SUBSCRIPTION_ID]${subscription_id}"
```
  > Note that you will have to update this code snippet with the respective service connection names, depending on which Databricks workspace you are deploying assets to.

5. Create two separate Azure Pipelines under your Azure DevOps project using the ‘Existing Azure Pipelines YAML file’ option. One of these Pipelines will use the `{{template `project_name` .}}-tests-ci.yml` script, and the other will use the `{{template `project_name` .}}-bundle-cicd.yml` script. See [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline) for more details on creating Azure Pipelines.
6. Define two build validation branch policies for the `{{template `default_branch` .}}` using the two Azure Pipelines created in step 1. This is required so that any PR changes to the `{{template `default_branch` .}}` must build successfully before PRs can complete.
  {{ end }}
{{ end }}

{{- if (eq .input_include_mlflow_recipes `yes`) }}
## Configure profiles for tests, staging, and prod
Address the TODOs in the following files:
* [databricks-dev.yaml](../{{template `project_name_alphanumeric_underscore` .}}/training/profiles/databricks-dev.yaml): specify recipe configs to use in dev workspace
* [databricks-staging.yaml](../{{template `project_name_alphanumeric_underscore` .}}/training/profiles/databricks-staging.yaml): specify recipe configs to use in recurring model training and batch inference
  jobs that run in the staging workspace
* [databricks-prod.yaml](../{{template `project_name_alphanumeric_underscore` .}}/training/profiles/databricks-prod.yaml) specify recipe configs to use in recurring model training and batch inference
  jobs that run in the prod workspace
* [databricks-test.yaml](../{{template `project_name_alphanumeric_underscore` .}}/training/profiles/databricks-test.yaml): specify recipe configs to use in integration tests(CI)
{{- end }}

## Merge a PR with your initial ML code
Create and push a PR branch adding the ML code to the repository.

```
git checkout -b add-ml-code
git add .
git commit -m "Add ML Code"
git push upstream add-ml-code
```

Open a PR from the newly pushed branch. CI will run to ensure that tests pass
on your initial ML code. Fix tests if needed, then get your PR reviewed and merged.
After the pull request merges, pull the changes back into your local `{{template `default_branch` .}}`
branch:

```
git checkout {{template `default_branch` .}}
git pull upstream {{template `default_branch` .}}
```

{{ if not (eq .input_release_branch .input_default_branch) -}}
## Create release branch
Create and push a release branch called `{{template `release_branch` .}}` off of the `{{template `default_branch` .}}` branch of the repository:
```
git checkout -b {{template `release_branch` .}} {{template `default_branch` .}}
git push upstream {{template `release_branch` .}}
git checkout {{template `default_branch` .}}
```

Your production jobs (model training, batch inference) will pull ML code against this branch, while your staging jobs will pull ML code against the `{{template `default_branch` .}}` branch. Note that the `{{template `default_branch` .}}` branch will be the source of truth for ML asset configs and CI/CD workflows.

For future ML code changes, iterate against the `{{template `default_branch` .}}` branch and regularly deploy your ML code from staging to production by merging code changes from the `{{template `default_branch` .}}` branch into the `{{template `release_branch` .}}` branch.
{{ end -}}

## Deploy ML assets and enable production jobs
Follow the instructions in [{{template `project_name` .}}/assets/README.md](../{{template `project_name_alphanumeric_underscore` .}}/assets/README.md) to deploy ML assets
and production jobs.

## Next steps
After you configure CI/CD and deploy training & inference pipelines, notify data scientists working
on the current project. They should now be able to follow the
[ML pull request guide](ml-pull-request.md) and [ML asset config guide](../{{template `project_name_alphanumeric_underscore` .}}/assets/README.md)  to propose, test, and deploy
ML code and pipeline changes to production.
