resource "databricks_git_credential" "service_principal_git_token" {
  git_username          = "{{cookiecutter.project_name}}-cicd"
  git_provider          = var.git_provider
  personal_access_token = var.git_token
}

{% if cookiecutter.cicd_platform == "gitHub" -%}
// Store Git token for triggering CD workflows in a Databricks secret scope for
// use by model training, in the staging and prod workspaces. We create the
// secret scopes using our CI/CD service principals, so that only the CI/CD service
// principals can access the scopes.
resource "databricks_secret_scope" "cd_credentials" {
  name = "${var.env}-{{cookiecutter.project_name}}-cd-credentials"
}

resource "databricks_secret" "cd_credentials_token" {
  key          = "token"
  string_value = var.git_token
  scope        = databricks_secret_scope.cd_credentials.id
}

resource "databricks_secret" "cd_github_repo" {
  key = "github_repo"
  // Extract the 'organization/repo' substring used to identify the repo
  string_value = replace(var.github_repo_url, "https://github.com/", "")
  scope        = databricks_secret_scope.cd_credentials.id
}
{% endif %}
