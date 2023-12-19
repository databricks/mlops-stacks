# MLOps Stacks Customization Guide
We provide the default MLOps Stack in this repo as a production-friendly starting point for MLOps.

For generic enhancements not specific to your organization
(e.g. add support for a new CI/CD provider), we encourage you to consider contributing the
change back to the MLOps Stacks repo, so that the community can help maintain and enhance it.

However, in many cases you may need to customize the stack, for example if:
* You have different Databricks workspace environments (e.g. a "test" workspace for CI, in addition to dev/staging/prod)
* You'd like to run extra checks/tests in CI/CD besides the ones supported out of the box
* You're using an ML code structure built in-house

For more information about generating a project using Databricks asset bundle templates, please refer to [link](https://docs.databricks.com/en/dev-tools/bundles/templates.html).

## Creating a custom stack

**Note**: the development loop for your custom stack is the same as for iterating on the
default stack. Before getting started, we encourage you to read
the [contributor guide](README.md#contributing) to learn how to
make, preview, and test changes to your custom stack.

### Fork the MLOps Stacks repo
Fork the MLOps Stacks repo. You may want to create a private fork if you're tailoring
the stack to the specific needs of your organization, or a public fork if you're creating
a generic new stack.

### (optional) Set up CI
Tests for MLOps Stacks are defined under the `tests/` directory and are
executed in CI by Github Actions workflows defined under `.github/`. We encourage you to configure
CI in your own MLOps Stacks repo to ensure it continues to work as you make changes.
If you use GitHub Actions for CI, the provided workflows should work out of the box.
Otherwise, you'll need to translate the workflows under `.github/` to the CI provider of your
choice.

### Update MLOps Stacks parameters
Update parameters in your fork as needed in `databricks_template_schema.json` and update corresponding template variable in `library/template_variables.tmpl`. Pruning the set of
parameters makes it easier for data scientists to start new projects, at the cost of reduced flexibility.

For example, you may have a fixed set of staging & prod Databricks workspaces (or use a single staging & prod workspace), so the
`input_databricks_staging_workspace_host` and `input_databricks_prod_workspace_host` parameters may be unnecessary. You may
also run all of your ML pipelines on a single cloud, in which case the `input_cloud` parameter is unnecessary.

The easiest way to prune parameters and replace them with hardcoded values is to follow
the [contributor guide](README.md#previewing-changes) to generate an example project with
parameters substituted-in, and then copy the generated project contents back into your MLOps Stacks repo.

## Customize individual components

### Example ML code
MLOps Stacks provides example ML code.
You may want to customize the example code, e.g. further prune it down into a skeleton for data scientists
to fill out.

If you customize this component, you can still use the CI/CD and ML asset components to build production ML pipelines, as long as you provide ML
notebooks with the expected interface. For example, model training under ``template/{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/training/notebooks/`` and inference under
``template/{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/deployment/batch_inference/notebooks/``. See code comments in the notebook files for the expected interface & behavior of these notebooks.

You may also want to update developer-facing docs under `template/{{.input_root_dir}}/docs/ml-developer-guide.md`
or `template/{{.input_root_dir}}/docs/ml-developer-guide-fs.md`, which will be read by users of your stack.

### CI/CD workflows
MLOps Stacks currently has the following sub-components for CI/CD:
* CI/CD workflow logic defined under `template/{{.input_root_dir}}/.github/` for testing and deploying ML code and models
* Logic to trigger model deployment through REST API calls to your CD system, when model training completes.
  This logic is currently captured in ``template/{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/deployment/model_deployment/notebooks/ModelDeployment.py``

### ML asset configs
Root ML asset config file can be found as ``{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/databricks.yml``. 
It defines the ML config assets to be included and workspace host for each deployment target.

ML asset configs (databricks CLI bundles code definitions of ML jobs, experiments, models etc) can be found under 
``template/{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/assets``, along with docs.

You can update this component to customize the default ML pipeline structure for new ML projects in your organization,
e.g. add additional model inference jobs or modify the default instance type used in ML jobs.

When updating this component, you may want to update developer-facing docs in
``template/{{.input_root_dir}}/{{template `project_name_alphanumeric_underscore` .}}/assets/README.md``.

### Docs
After making customizations, make any changes needed to
the docs under `template/{{.input_root_dir}}/docs` and in the main README
(`template/{{.input_root_dir}}/README.md`) to reflect any updates you've made to the MLOps Stacks repo.
For example, you may want to include a link to your custom MLOps Stacks repo in `template/{{.input_root_dir}}/README.md`.
