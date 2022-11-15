# MLOps Setup Guide
[(back to main README)](../README.md)

## Table of contents
* [Intro](#intro)
* [Create a hosted Git repo](#create-a-hosted-git-repo)
* [Configure CI/CD and ML resource state storage](#configure-cicd-and-ml-resource-state-storage)
* [Merge PR with initial ML code](#merge-a-pr-with-your-initial-ml-code)
{% if cookiecutter.release_branch != cookiecutter.default_branch -%}
* [Create release branch](#create-release-branch)
{% endif -%}
* [Deploy ML resources and enable production jobs](#deploy-ml-resources-and-enable-production-jobs)
* [Next steps](#next-steps)

## Intro
This page explains how to productionize the current project, setting up CI/CD and
ML resource deployment, and deploying ML training and inference jobs.

After following this guide, data scientists can follow the [ML Pull Request](./ml-pull-request.md) and 
[ML Config](../databricks-config/README.md) guides to make changes to ML code or deployed jobs.

## Create a hosted Git repo
Create a hosted Git repo to store project code, if you haven't already done so. From within the project
directory, initialize git and add your hosted Git repo as a remote:
```
git init --initial-branch={{cookiecutter.default_branch}}
```

```
git remote add upstream <hosted-git-repo-url>
```

Commit the current README file and other docs to the `{{cookiecutter.default_branch}}` branch of the repo, to enable forking the repo:
```
git add README.md docs .gitignore .mlops-setup-scripts databricks-config/README.md
git commit -m "Adding project README"
git push upstream {{cookiecutter.default_branch}}
```

## Configure CI/CD and ML resource state storage
Follow the guide in [.mlops-setup-scripts/README.md](../.mlops-setup-scripts/README.md) to
configure and enable CI/CD for the hosted Git repo created in the previous step, as well as
set up a state storage backend for ML resources (jobs, experiments, etc) created for the
current ML project.

{%- if cookiecutter.include_feature_store == "no" %}
## Configure profiles for tests, staging, and prod
Address the TODOs in the following files:
* [databricks-test.yaml](../profiles/databricks-test.yaml): specify recipe configs to use in integration tests
* [databricks-staging.yaml](../profiles/databricks-staging.yaml): specify recipe configs to use in recurring model training and batch inference
  jobs that run in the staging workspace
* [databricks-prod.yaml](../profiles/databricks-prod.yaml) specify recipe configs to use in recurring model training and batch inference
  jobs that run in the prod workspace
{%- endif %}

## Merge a PR with your initial ML code
Create and push a PR branch adding the ML code to the repository.
We recommend including all files outside of `databricks-config` in this PR:

```
git checkout -b add-ml-code
git add -- . ':!databricks-config'
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

Your production jobs (model training, batch inference) will pull ML code against this branch, while your staging jobs will pull ML code against the `{{cookiecutter.default_branch}}` branch. Note that the `{{cookiecutter.default_branch}}` branch will be the source of truth for ML resource configurations and CI/CD workflows.

For future ML code changes, iterate against the `{{cookiecutter.default_branch}}` branch and regularly deploy your ML code from staging to production by merging code changes from the `{{cookiecutter.default_branch}}` branch into the `{{cookiecutter.release_branch}}` branch.
{% endif -%}

## Deploy ML resources and enable production jobs
Follow the instructions in [databricks-config/README.md](../databricks-config/README.md) to deploy ML resources
and production jobs.

## Next steps
After you configure CI/CD and deploy training & inference pipelines, notify data scientists working
on the current project. They should now be able to follow the
[ML pull request guide](./ml-pull-request.md) and [ML resource config guide](../databricks-config/README.md) to propose, test, and deploy
ML code and pipeline changes to production.
