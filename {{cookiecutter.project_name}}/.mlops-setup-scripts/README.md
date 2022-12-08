# MLOps Setup Scripts
[(back to MLOps setup guide)](../docs/mlops-setup.md)

This directory contains setup scripts intended to automate CI/CD and ML resource config setup
for MLOps engineers.

{% if cookiecutter.cicd_platform == "gitHub" -%}
The scripts set up CI/CD with GitHub Actions. If using another CI/CD provider, you can
easily translate the provided CI/CD workflows (GitHub Actions YAML under `.github/workflows`)
to other CI/CD providers by running the same shell commands, with a few caveats:

* Usages of the `run-notebook` Action should be replaced by [installing the Databricks CLI](https://github.com/databricks/databricks-cli#installation)
  and invoking the `databricks runs submit --wait` CLI
  ([docs]({{ "dev-tools/cli/runs-cli.html#submit-a-one-time-run" | generate_doc_link(cookiecutter.cloud) }})).
* The model deployment CD workflows in `deploy-model-prod.yml` and `deploy-model-staging.yml` are currently triggered
  by the `notebooks/TriggerModelDeploy.py` helper notebook after the model training job completes. This notebook
  hardcodes the API endpoint for triggering a GitHub Actions workflow. Update `notebooks/TriggerModelDeploy.py`
  to instead hit the appropriate REST API endpoint for triggering model deployment CD for your CI/CD provider.

{% elif cookiecutter.cicd_platform == "azureDevOpsServices" -%}
The bootstrap steps use Terraform to set up the following in an automated manner:
1. Create an Azure Blob Storage container for storing ML resource config (job, MLflow experiment, etc) state for the
   current ML project.
2. Create another Azure Blob Storage container for storing the state of CI/CD principals provisioned for the current
   ML project.
3. Write credentials for accessing the container in (1) to a file.
4. Create Databricks service principals configured for CI/CD, write their credentials to a file, and store their
   state in the Azure Blob Storage container created in (2).
5. Create the two following Azure DevOps Pipelines along with required variable group:
    * `testing_ci` - Unit tests and integration tests triggered upon PR to the {{cookiecutter.default_branch}} branch.
    * `terraform_cicd` - Continuous integration for Terraform triggered upon a PR to {{cookiecutter.default_branch}} and changes to `databricks-config`, 
                         followed by continuous deployment of changes upon successfully merging into {{cookiecutter.default_branch}}.
6. Create build validation policies defining requirements when PRs are submitted to the default branch of your repository.        
{% endif -%}
      
## Prerequisites

### Install CLIs
* Install the [Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli)
  * Requirement: `terraform >=1.2.7`
* Install the [Databricks CLI](https://github.com/databricks/databricks-cli): ``pip install databricks-cli``
    * Requirement: `databricks-cli >= 0.17`
{% if cookiecutter.cloud == "azure" -%}
* Install Azure CLI: ``pip install azure-cli``
    * Requirement: `azure-cli >= 2.39.0`
{% elif cookiecutter.cloud == "aws" -%}
* Install AWS CLI: ``pip install awscli``
{%- endif %}

### Verify permissions
To use the scripts, you must:
* Be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console]({{cookiecutter.databricks_staging_workspace_host}}#setting/accounts) and
  [prod workspace admin console]({{cookiecutter.databricks_prod_workspace_host}}#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.
* Be able to create Git tokens with permission to check out the current repository
{% if cookiecutter.cloud == "azure" -%}
* Determine the Azure AAD tenant (directory) ID and subscription associated with your staging and prod workspaces,
  and verify that you have at least [Application.ReadWrite.All](https://docs.microsoft.com/en-us/graph/permissions-reference#application-resource-permissions) permissions on
  the AAD tenant and ["Contributor" permissions](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#all) on
  the subscription. To do this:
    1. Navigate to the [Azure Databricks resource page](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Databricks%2Fworkspaces) in the Azure portal. Ensure there are no filters configured in the UI, i.e. that
       you're viewing workspaces across all Subscriptions and Resource Groups.
    2. Search for your staging and prod workspaces by name to verify that they're part of the current directory. If you don't know the workspace names, you can log into the
       [staging workspace]({{cookiecutter.databricks_staging_workspace_host}}) and [prod workspace]({{cookiecutter.databricks_prod_workspace_host}}) and use the
       [workspace switcher]({{ 'workspace/#switch-to-a-different-workspace' | generate_doc_link(cookiecutter.cloud) }}) to view
       the workspace name
    3. If you can't find the workspaces, switch to another directory by clicking your profile info in the top-right of the Azure Portal, then
       repeat steps i) and ii). If you still can't find the workspace, ask your Azure account admin to ensure that you have
       at least ["Contributor" permissions](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#all)
       on the subscription containing the workspaces. After confirming that the staging and prod workspaces are in the current directory, proceed to the next steps.
    4. The [Azure Databricks resource page](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Databricks%2Fworkspaces)
       contains links to the subscription containing your staging and prod workspaces. Click into the subscription, copy its ID ("Subscription ID"), and
       store it as an environment variable by running `export AZURE_SUBSCRIPTION_ID=<subscription-id>`
    5. Verify that you have "Contributor" access by clicking into
       "Access Control (IAM)" > "View my access" within the subscription UI,
       as described in [this doc page](https://docs.microsoft.com/en-us/azure/role-based-access-control/check-access#step-1-open-the-azure-resources).
       If you don't have [Contributor permissions](https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#all),
       ask an Azure account admin to grant access.
    6. Find the current tenant ID
       by navigating to [this page](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Properties),
       also accessible by navigating to the [Azure Active Directory UI](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview)
       and clicking Properties. Save the tenant ID as an environment variable by running `export AZURE_TENANT_ID=<id>`
    7. Verify that you can create and manage service principals in the AAD tenant, by opening the
       [App registrations UI](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps)
       under the Azure Active Directory resource within the Azure portal. Then, verify that you can click "New registration" to create
       a new AAD application, but don't actually create one. If unable to click "New registration", ask your Azure admin to grant you [Application.ReadWrite.All](https://docs.microsoft.com/en-us/graph/permissions-reference#application-resource-permissions) permissions
  {% elif cookiecutter.cloud == "aws" -%}
* Have permission to manage AWS IAM users and attached IAM policies (`"iam:*"` permissions) in the current AWS account.
  If you lack sufficient permissions, you'll see an error message describing any missing permissions when you
  run the setup scripts below. If that occurs, contact your AWS account admin to request any missing permissions.
{%- endif %}

{% if cookiecutter.cloud == "azure" -%}
### Configure Azure auth
* Log into Azure via `az login --tenant "$AZURE_TENANT_ID"`
* Run `az account set --subscription "$AZURE_SUBSCRIPTION_ID"` to set the active Azure subscription
{% elif cookiecutter.cloud == "aws" -%}
### Configure AWS auth
* After verifying that your AWS user has permission to manage IAM users and policies,
  follow [these docs](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
  to generate an AWS access key.
* Run `aws configure --profile {{cookiecutter.project_name}}` to configure an AWS CLI profile, passing the access key ID and secret access key from the previous step
* Run `export AWS_PROFILE={{cookiecutter.project_name}}` to indicate to Terraform that it should use the newly-created AWS CLI profile
  to authenticate to AWS
{%- endif %}

### Configure Databricks auth
* Configure a Databricks CLI profile for your staging workspace by running
  ``databricks configure --token --profile "{{cookiecutter.project_name}}-staging" --host {{cookiecutter.databricks_staging_workspace_host}}``, 
  which will prompt you for a REST API token
* Create a [Databricks REST API token]({{ "dev-tools/api/latest/authentication.html#generate-a-personal-access-token" | generate_doc_link(cookiecutter.cloud) }})
  in the staging workspace ([link]({{cookiecutter.databricks_staging_workspace_host}}#setting/account))
  and paste the value into the prompt.
* Configure a Databricks CLI for your prod workspace by running ``databricks configure --token --profile "{{cookiecutter.project_name}}-prod" --host {{cookiecutter.databricks_prod_workspace_host}}``
* Create a Databricks REST API token in the prod workspace ([link]({{cookiecutter.databricks_prod_workspace_host}}#setting/account)).
  and paste the value into the prompt

{% if cookiecutter.cloud == "aws" -%}
### Set up service principal user group
Ensure a group named `{{cookiecutter.service_principal_group}}` exists in the staging and prod workspace, e.g.
by checking for the group in the [staging workspace admin console]({{cookiecutter.databricks_staging_workspace_host}}#setting/accounts/groups) and
[prod workspace admin console]({{cookiecutter.databricks_prod_workspace_host}}#setting/accounts/groups).
Create the group in staging and/or prod as needed.
Then, grant the `{{cookiecutter.service_principal_group}}` group [token usage permissions]({{ "administration-guide/access-control/tokens.html#manage-token-permissions-using-the-admin-console" | generate_doc_link(cookiecutter.cloud) }})
{% endif -%}

### Obtain a git token for use in CI/CD
The setup script prompts a Git token with both read and write permissions
on the current repo.

{% if cookiecutter.cicd_platform == "gitHub" -%}
This token is used to:
1. Fetch ML code from the current repo to run on Databricks for CI/CD (e.g. to check out code from a PR branch and run it
during CI/CD).
2. Call back from
   Databricks -> GitHub Actions to trigger a model deployment deployment workflow when
   automated model retraining completes, i.e. perform step (2) in
   [this diagram](https://github.com/databricks/mlops-stack/blob/main/Pipeline.md#model-training-pipeline).
   
If using GitHub as your hosted Git provider, you can generate a Git token through the [token UI](https://github.com/settings/tokens/new);
be sure to generate a token with "Repo" scope. If you have SSO enabled with your Git provider, be sure to authorize your token.

{% elif cookiecutter.cicd_platform == "azureDevOpsServices" -%}
This token is used to fetch ML code from the current repo to run on Databricks for CI/CD (e.g. to check out code from a PR branch and run it
during CI/CD). You can generate a PAT token for Azure DevOps by following the steps described [here](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows).
Ensure your PAT (at a minimum) has the following permissions:
- **Build**: Read & execute
- **Code**: Read, write & manage
- **Project and Team**: Read
- **Token Administration**: Read & manage
- **Tokens**: Read & manage
- **Variable Groups**: Read, Create, & Manage
- **Work Items**: Read

### Update permissions for the build service
In our CI/CD workflow, upon successfully merging a PR with changes to `databricks-config/**` the CD step will trigger the
Terraform deploy stage of our pipeline. Within this pipeline `git` commands are run to commit and modify Terraform output files. 
To enable this workflow you must update the permissions of our build service. Within your **Project Settings**, select **Repostiories**.
Go to the name of your repository and select **Security**. For the user `{{cookiecutter.project_name}} Build Service (<your-username>)` grant the following:
- **Bypass policies when completing pull requests**: Allow
- **Bypass policies when pushing**: Allow
- **Contribute:** Allow
- **Create branch:** Allow
- **Create tag:** Allow
- **Read:** Allow

{% endif -%}


## Usage

### Run the scripts
From the repo root directory, run:

```
{% if cookiecutter.cloud == "aws" -%}
# Set AWS_REGION environment variable to your desired AWS region for storing
# terraform state, e.g. "us-east-1" to store Terraform state in S3 buckets in us-east-1
# NOTE: if you supply an AWS region other than us-east-1, be sure to update the
# AWS region specified in databricks-config/staging/provider.tf and databricks-config/prod/provider.tf
# to match
export AWS_REGION="us-east-1"
{% endif -%}
python .mlops-setup-scripts/terraform/bootstrap.py
```
{% if cookiecutter.cicd_platform == "azureDevOpsServices" -%}
This initial bootstrap will produce an ARM access key. This key is required as a variable in the next step. To view this
key locally and copy the key for this step you can do the following `vi ~/.{{cookiecutter.project_name}}-cicd-terraform-secrets.json`.
{% endif -%}

Then, run the following command, providing the required vars to bootstrap CI/CD.
```
python .mlops-setup-scripts/cicd/bootstrap.py \
{%- if cookiecutter.cloud == "azure" %}
  --var azure_tenant_id="$AZURE_TENANT_ID" \
{%- endif %}
{%- if cookiecutter.cicd_platform == "gitHub" %}
  --var github_repo_url=https://github.com/<your-org>/<your-repo-name> \
  --var git_token=<your-git-token>
{%- elif cookiecutter.cicd_platform == "azureDevOpsServices" %}
  --var azure_devops_org_url=https://dev.azure.com/<your-org-name> \
  --var azure_devops_project_name=<name-of-project> \
  --var azure_devops_repo_name=<name-of-repo> \
  --var git_token=<your-git-token> \
  --var arm_access_key=<arm-access-key> 
{%- endif %}
```

Take care to run the Terraform bootstrap script before the CI/CD bootstrap script. 

The first Terraform bootstrap script will:

{% if cookiecutter.cloud == "azure" %}
1. Create an Azure Blob Storage container for storing ML resource config (job, MLflow experiment, etc) state for the
   current ML project
2. Create another Azure Blob Storage container for storing the state of CI/CD principals provisioned for the current
   ML project
   
The second CI/CD bootstrap script will:

3. Write credentials for accessing the container in (1) to a file
4. Create Databricks service principals configured for CI/CD, write their credentials to a file, and store their
   state in the Azure Blob Storage container created in (2).
{% if cookiecutter.cicd_platform == "azureDevOpsServices" %}
5. Create the two following Azure DevOps Pipelines along with required variable group:
    * `testing_ci` - Unit tests and integration tests triggered upon PR to the {{cookiecutter.default_branch}} branch.
    * `terraform_cicd` - Continuous integration for Terraform triggered upon a PR to {{cookiecutter.default_branch}} and changes to `databricks-config`, 
                         followed by continuous deployment of changes upon successfully merging into {{cookiecutter.default_branch}}.
6. Create build validation policies defining requirements when PRs are submitted to the default branch of your repository.        
{% endif %}
   
{% elif cookiecutter.cloud == "aws" %}
1. Create an AWS S3 bucket and DynamoDB table for storing ML resource config (job, MLflow experiment, etc) state for the
   current ML project
2. Create another AWS S3 bucket and DynamoDB table for storing the state of CI/CD principals provisioned for the current
   ML project. 
   
The second CI/CD bootstrap script will:

3. Write credentials for accessing the S3 bucket and Dynamo DB table in (1) to a file.
4. Create Databricks service principals configured for CI/CD, write their credentials to a file, and store their
   state in the S3 bucket and DynamoDB table created in (2). 
{% endif %}

Each `bootstrap.py` script will print out the path to a JSON file containing generated secret values
to store for CI/CD. **Note the paths of these secrets files for subsequent steps.** If either script
fails or the generated resources are misconfigured (e.g. you supplied invalid Git credentials for CI/CD
service principals when prompted), simply rerun and supply updated input values.

{% if cookiecutter.cicd_platform == "gitHub" %}
### Store generated secrets in CI/CD
Store each of the generated secrets in the output JSON files as
[GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository),
where the JSON key
{% if cookiecutter.cloud == "azure" -%}
(e.g. `prodAzureSpApplicationId`)
{% elif cookiecutter.cloud == "aws" -%}
(e.g. `PROD_WORKSPACE_TOKEN`)
{% endif -%} 
is the expected name of the secret in GitHub Actions and the JSON value
(without the surrounding `"` double-quotes) is the value of the secret. 

Note: The provided GitHub Actions workflows under `.github/workflows` assume that you will configure
[repo secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository),
but you can also use
[environment secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment)
to restrict access to production secrets. You can also modify the workflows to read secrets from another
secret provider.
{% endif %}

{% if cookiecutter.cicd_platform == "gitHub" %}
### Add GitHub workflows to hosted Git repo
Create and push a PR branch adding the GitHub Actions workflows under `.github`:

```
git checkout -b add-cicd-workflows
git add .github
git commit -m "Add CI/CD workflows"
git push upstream add-cicd-workflows
```

Follow [GitHub docs](https://docs.github.com/en/actions/managing-workflow-runs/disabling-and-enabling-a-workflow#enabling-a-workflow)
to enable workflows on your PR. Then, open and merge a pull request based on your PR branch to add the CI/CD workflows to your hosted Git Repo.

{% elif cookiecutter.cicd_platform == "azureDevOpsServices" %}
### Add Azure DevOps pipelines to hosted Git repo
Create and push a PR branch adding the Azure DevOps Pipelines under `.azure`:

```
git checkout -b add-cicd-workflows
git add .azure
git commit -m "Add CI/CD workflows"
git push upstream add-cicd-workflows
```

Follow [Azure DevOps docs](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines?view=azure-devops) 
to learn how to create an Azure DevOps build pipeline. Then, open and merge a pull request based on your PR branch to add the CI/CD workflows to your hosted Git Repo.
{% endif %}

Note that the CI/CD workflows will fail
until ML code is introduced to the repo in subsequent steps - you should
merge the pull request anyways.

After the pull request merges, pull the changes back into your local `{{cookiecutter.default_branch}}`
branch:

```
git checkout {{cookiecutter.default_branch}}
git pull upstream {{cookiecutter.default_branch}}
```

{% if cookiecutter.cicd_platform == "gitHub" %}
Finally, [create environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)
in your repo named "staging" and "prod"
{% elif cookiecutter.cicd_platform == "azureDevOpsServices" %}
Finally, [create environments](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops)
in your repo named "staging" and "prod"
{% endif %}

### Secret rotation
The generated CI/CD
{% if cookiecutter.cloud == "aws" -%}
Databricks service principal REST API tokens have an [expiry of 100 days](https://github.com/databricks/terraform-databricks-mlops-aws-project#mlops-aws-project-module)
{% elif cookiecutter.cloud == "azure" -%}
Azure application client secrets have an expiry of [2 years](https://github.com/databricks/terraform-databricks-mlops-azure-project-with-sp-creation#outputs)
{% endif -%}
and will need to be rotated thereafter. To rotate CI/CD secrets after expiry, simply rerun `python .mlops-setup-scripts/cicd/bootstrap.py`
with updated inputs, after configuring auth as described in the prerequisites.

## Next steps
In this project, interactions with the staging and prod workspace are driven through CI/CD. After you've configured
CI/CD and ML resource state storage, you can productionize your ML project by testing and deploying ML code, deploying model training and
inference jobs, and more. See the [MLOps setup guide](../docs/mlops-setup.md) for details.
