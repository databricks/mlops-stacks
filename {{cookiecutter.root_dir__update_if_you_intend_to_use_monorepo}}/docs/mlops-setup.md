# MLOps Setup Guide
[(back to main README)](../README.md)

## Table of contents
* [Intro](#intro)
* [Create a hosted Git repo](#create-a-hosted-git-repo)
* [Configure CI/CD](#configure-cicd)
{%- if cookiecutter.include_feature_store == "no" %}
* [Configure profiles for tests, staging, and prod](#configure-profiles-for-tests-staging-and-prod){% endif %}
* [Merge PR with initial ML code](#merge-a-pr-with-your-initial-ml-code)
{% if cookiecutter.release_branch != cookiecutter.default_branch -%}
* [Create release branch](#create-release-branch)
{% endif -%}
* [Deploy ML resources and enable production jobs](#deploy-ml-resources-and-enable-production-jobs)
* [Next steps](#next-steps)

## Intro
This page explains how to productionize the current project, setting up CI/CD and
ML resource deployment, and deploying ML training and inference jobs.

After following this guide, data scientists can follow the [ML Pull Request](ml-pull-request.md) and
[ML Config](../{{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md)  guides to make changes to ML code or deployed jobs.

## Create a hosted Git repo
Create a hosted Git repo to store project code, if you haven't already done so. From within the project
directory, initialize Git and add your hosted Git repo as a remote:
```
git init --initial-branch={{cookiecutter.default_branch}}
```

```
git remote add upstream <hosted-git-repo-url>
```

Commit the current README file and other docs to the `{{cookiecutter.default_branch}}` branch of the repo, to enable forking the repo:
```
git add README.md docs .gitignore {{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md
git commit -m "Adding project README"
git push upstream {{cookiecutter.default_branch}}
```

## Configure CI/CD

### Prerequisites
* You must be an account admin to add service principals to the account.
* You must be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console]({{cookiecutter.databricks_staging_workspace_host}}#setting/accounts) and
  [prod workspace admin console]({{cookiecutter.databricks_prod_workspace_host}}#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.

### Set up authentication for CI & CD
#### Set up Service Principal
{% if cookiecutter.cloud == "azure" %}
To authenticate and manage ML resources created by CI and CD, a
[service principals]({{ "administration-guide/users-groups/service-principals"  | generate_doc_link(cookiecutter.cloud) }})
for the project should be created and added to both staging and prod workspaces. Follow
[Add a service principal to your Azure Databricks account]({{ "administration-guide/users-groups/service-principals#--add-a-service-principal-to-your-azure-databricks-account"  | generate_doc_link(cookiecutter.cloud) }})
and [Add a service principal to a workspace]({{ "administration-guide/users-groups/service-principals#--add-a-service-principal-to-a-workspace"  | generate_doc_link(cookiecutter.cloud) }})
for details.

For your convenience, we also have Terraform modules that can be used to [create](https://registry.terraform.io/modules/databricks/mlops-azure-project-with-sp-creation/databricks/latest) or [link](https://registry.terraform.io/modules/databricks/mlops-azure-project-with-sp-linking/databricks/latest) service principals.

{% elif cookiecutter.cloud == "aws" %}
To authenticate and manage ML resources created by CI and CD, a
[service principals]({{ "administration-guide/users-groups/service-principals.html"  | generate_doc_link(cookiecutter.cloud) }})
for the project should be created in and added to both staging and prod workspaces. Follow
[Add a service principal to your Databricks account]({{ "administration-guide/users-groups/service-principals.html#add-a-service-principal-to-your-databricks-account"  | generate_doc_link(cookiecutter.cloud) }})
and [Add a service principal to a workspace]({{ "administration-guide/users-groups/service-principals.html#add-a-service-principal-to-a-workspace"  | generate_doc_link(cookiecutter.cloud) }})
for details.

For your convenience, we also have a [Terraform module](https://registry.terraform.io/modules/databricks/mlops-aws-project/databricks/latest) that can set up your service principals.
{% endif %}

#### Set secrets for CI & CD
{% if cookiecutter.cicd_platform == "gitHub" and cookiecutter.cloud == "aws" %}
After creating a service principal and adding it to the staging and prod workspaces, follow
[Manage access tokens for a service principal]({{ "administration-guide/users-groups/service-principals.html#manage-access-tokens-for-a-service-principal"  | generate_doc_link(cookiecutter.cloud) }})
to get service principal tokens for staging and prod workspace and [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
to add the following secrets to gitHub:
- STAGING_WORKSPACE_TOKEN : service principal token for staging workspace
- PROD_WORKSPACE_TOKEN : service principal token for prod workspace
  {% endif %}

{% if cookiecutter.cicd_platform == "gitHub" and cookiecutter.cloud == "azure" %}
After creating a service principal and add it to the staging and prod workspaces, refer to
[Manage access tokens for a service principal]({{ "administration-guide/users-groups/service-principals#--manage-access-tokens-for-a-service-principal"  | generate_doc_link(cookiecutter.cloud) }})
and [Get Azure AD tokens for service principals]({{ "dev-tools/api/latest/aad/service-prin-aad-token"  | generate_doc_link(cookiecutter.cloud) }})
to get service principal (tenant id, application id, client secret) for staging and prod workspace and [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
to add the following secrets to gitHub:
- PROD_AZURE_SP_TENANT_ID
- PROD_AZURE_SP_APPLICATION_ID
- PROD_AZURE_SP_CLIENT_SECRET
- STAGING_AZURE_SP_TENANT_ID
- STAGING_AZURE_SP_APPLICATION_ID
- STAGING_AZURE_SP_CLIENT_SECRET
  {% endif %}

{% if cookiecutter.cicd_platform == "azureDevOpsServices" %}
After creating a service principal and add it to the staging and prod workspaces, refer to
[Manage access tokens for a service principal]({{ "administration-guide/users-groups/service-principals#--manage-access-tokens-for-a-service-principal"  | generate_doc_link(cookiecutter.cloud) }})
and [Get Azure AD tokens for service principals]({{ "dev-tools/api/latest/aad/service-prin-aad-token"  | generate_doc_link(cookiecutter.cloud) }})
to get service principal (tenant id, application id, client secret) for staging and prod workspace and [Set secret variables](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/set-secret-variables?view=azure-devops&tabs=yaml%2Cbash)
to add the following secret variables to Azure DevOps:
- PROD_AZURE_SP_TENANT_ID
- PROD_AZURE_SP_APPLICATION_ID
- PROD_AZURE_SP_CLIENT_SECRET
- STAGING_AZURE_SP_TENANT_ID
- STAGING_AZURE_SP_APPLICATION_ID
- STAGING_AZURE_SP_CLIENT_SECRET
  {% endif %}

{%- if cookiecutter.include_feature_store == "no" %}
## Configure profiles for tests, staging, and prod
Address the TODOs in the following files:
* [databricks-dev.yaml](../{{cookiecutter.project_name_alphanumeric_underscore}}/training/profiles/databricks-dev.yaml): specify recipe configs to use in dev workspace
* [databricks-staging.yaml](../{{cookiecutter.project_name_alphanumeric_underscore}}/training/profiles/databricks-staging.yaml): specify recipe configs to use in recurring model training and batch inference
  jobs that run in the staging workspace
* [databricks-prod.yaml](../{{cookiecutter.project_name_alphanumeric_underscore}}/training/profiles/databricks-prod.yaml) specify recipe configs to use in recurring model training and batch inference
  jobs that run in the prod workspace
* [databricks-test.yaml](../{{cookiecutter.project_name_alphanumeric_underscore}}/training/profiles/databricks-test.yaml): specify recipe configs to use in integration tests(CI)
{%- endif %}

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
After the pull request merges, pull the changes back into your local `{{cookiecutter.default_branch}}`
branch:

```
git checkout {{cookiecutter.default_branch}}
git pull upstream {{cookiecutter.default_branch}}
```

{% if cookiecutter.release_branch != cookiecutter.default_branch -%}
## Create release branch
Create and push a release branch called `{{cookiecutter.release_branch}}` off of the `{{cookiecutter.default_branch}}` branch of the repository:
```
git checkout -b {{cookiecutter.release_branch}} {{cookiecutter.default_branch}}
git push upstream {{cookiecutter.release_branch}}
git checkout {{cookiecutter.default_branch}}
```

Your production jobs (model training, batch inference) will pull ML code against this branch, while your staging jobs will pull ML code against the `{{cookiecutter.default_branch}}` branch. Note that the `{{cookiecutter.default_branch}}` branch will be the source of truth for ML resource configs and CI/CD workflows.

For future ML code changes, iterate against the `{{cookiecutter.default_branch}}` branch and regularly deploy your ML code from staging to production by merging code changes from the `{{cookiecutter.default_branch}}` branch into the `{{cookiecutter.release_branch}}` branch.
{% endif -%}

## Deploy ML resources and enable production jobs
Follow the instructions in [{{cookiecutter.project_name}}/databricks-resources/README.md](../{{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md) to deploy ML resources
and production jobs.

## Next steps
After you configure CI/CD and deploy training & inference pipelines, notify data scientists working
on the current project. They should now be able to follow the
[ML pull request guide](ml-pull-request.md) and [ML resource config guide](../{{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md)  to propose, test, and deploy
ML code and pipeline changes to production.
