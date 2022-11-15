# Stack Customization Guide
We provide the default stack in this repo as a production-friendly starting point for MLOps.

For generic enhancements not specific to your organization
(e.g. add support for a new CI/CD provider), we encourage you to consider contributing the
change back to the default stack, so that the community can help maintain and enhance it.

However, in many cases you may need to customize the stack, for example if:
* You have different Databricks workspace environments (e.g. a "test" workspace for CI, in addition to dev/staging/prod)
* You'd like to run extra checks/tests in CI/CD besides the ones supported out of the box
* You're using an ML code structure built in-house

## Creating a custom stack

**Note**: the development loop for your custom stack is the same as for iterating on the
default stack. Before getting started, we encourage you to read
the [contributor guide](README.md#contributing) to learn how to
make, preview, and test changes to your custom stack.

### Fork the default stack repo
Fork the default stack repo. You may want to create a private fork if you're tailoring
the stack to the specific needs of your organization, or a public fork if you're creating
a generic new stack.

### (optional) Set up CI for your new stack
Tests for the default stack are defined under the `tests/` directory and are
executed in CI by Github Actions workflows defined under `.github/`. We encourage you to configure
CI in your own stack repo to ensure the stack continues to work as you make changes.
If you use GitHub Actions for CI, the provided workflows should work out of the box.
Otherwise, you'll need to translate the workflows under `.github/` to the CI provider of your
choice.

### Update stack parameters
Update parameters in your fork as needed in `cookiecutter.json`. Pruning the set of
parameters makes it easier for data scientists to start new projects, at the cost of reduced flexibility.

For example, you may have a fixed set of staging & prod Databricks workspaces (or use a single staging & prod workspace), so the
`databricks_staging_workspace_host` and `databricks_prod_workspace_host` parameters may be unnecessary. You may
also run all of your ML pipelines on a single cloud, in which case the `cloud` parameter is unnecessary.

The easiest way to prune parameters and replace them with hardcoded values is to follow
the [contributor guide](README.md#previewing-stack-changes) to generate an example project with
parameters substituted-in, and then copy the generated project contents back into your stack.

## Customize individual components

### Example ML code
The default stack provides example ML code using [MLflow recipes](https://mlflow.org/docs/latest/recipes.html#).
You may want to customize the example code, e.g. further prune it down into a skeleton for data scientists
to fill out, or remove and replace the use of MLflow Recipes if you expect data scientists to work on problem
types that are currently unsupported by MLflow Recipes.

If you customize this component, you can still use the CI/CD and ML resource components to build production ML pipelines, as long as you provide ML
notebooks with the expected interface for model training and inference under
`{{cookiecutter_project_name}}/notebooks/`. See code comments in files under
`{{cookiecutter_project_name}}/notebooks/` for the expected interface & behavior of these notebooks.

You may also want to update developer-facing docs under `{{cookiecutter.project_name}}/docs/ml-developer-guide.md`,
which will be read by users of your stack.

### CI/CD workflows
The default stack currently has the following sub-components for CI/CD:
* CI/CD workflow logic defined under `{{cookiecutter.project_name}}/.github/` for testing and deploying ML code and models
* Automated scripts and docs for setting up CI/CD under `{{cookiecutter.project_name}}/.mlops-setup-scripts/`
* Logic to trigger model deployment through REST API calls to your CD system, when model training completes.
  This logic is currently captured in `{{cookiecutter.project_name}}/notebooks/TriggerModelDeploy.py`

### ML resource config
ML resource config (Terraform code definitions of ML jobs, experiments, etc) can be found under
``{{cookiecutter.project_name}}/databricks-config``, along with docs. This component depends on
the MLOps setup scripts described above in the CI/CD component (`{{cookiecutter.project_name}}/.mlops-setup-scripts`).

You can update this component to customize the default ML pipeline structure for new ML projects in your organization,
e.g. add additional model inference jobs or modify the default instance type used in ML jobs.

When updating this component, you may want to update developer-facing docs in
`{{cookiecutter.project_name}}/databricks-config/README.md`.

### Docs
After making stack customizations, make any changes needed to
the stack docs under `{{cookiecutter.project_name}}/docs` and in the main README
(`{{cookiecutter.project_name}}/README.md`) to reflect any updates you've made to the stack.
For example, you may want to include a link to your custom stack in `{{cookiecutter.project_name}}/README.md`.
