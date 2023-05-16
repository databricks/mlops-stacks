# CI/CD Workflow Definitions
This directory contains CI/CD workflow definitions using [GitHub Actions](https://docs.github.com/en/actions),
under ``workflows``. These workflows cover testing and deployment of both ML code (for model training, batch inference, etc) and the 
Databricks ML resource definitions under ``{{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources``. 

To set up CI/CD for a new project,
please refer to [ML resource config - set up CI CD](../../{{cookiecutter.project_name_alphanumeric_underscore}}/databricks-resources/README.md#set-up-ci-and-cd).
