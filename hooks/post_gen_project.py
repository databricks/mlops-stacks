import os
import shutil


def remove_filepath(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)


project_name_alphanumeric_underscore = "{{cookiecutter.project_name_alphanumeric_underscore}}"
current_cloud = "{{cookiecutter.cloud}}"
cicd_platform = "{{cookiecutter.cicd_platform}}"
include_feature_store = "{{cookiecutter.include_feature_store}}"

mlp_paths = [
    os.path.join(project_name_alphanumeric_underscore, "training", "profiles"),
    os.path.join(project_name_alphanumeric_underscore, "training", "notebooks", "Train.py"),
    os.path.join(project_name_alphanumeric_underscore, "training", "recipe.yaml"),
    os.path.join(project_name_alphanumeric_underscore, "training", "README.md"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "training", "ingest_test.py"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "training", "split_test.py"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "training", "train_test.py"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "training", "test_sample.parquet"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "training", "transform_test.py"),
    os.path.join("docs", "ml-developer-guide.md"),
    os.path.join(".github", "workflows", "{{cookiecutter.project_name}}-run-tests.yml"),
]

feature_store_paths = [
    os.path.join(project_name_alphanumeric_underscore, "feature_engineering"),
    os.path.join(project_name_alphanumeric_underscore, "tests", "feature_engineering"),
    os.path.join(project_name_alphanumeric_underscore, "training", "notebooks", "TrainWithFeatureStore.py"),
    os.path.join(
        project_name_alphanumeric_underscore,
        "databricks-resources",
        "feature-engineering-workflow-resource.yml"
    ),
    os.path.join(".github", "workflows", "{{cookiecutter.project_name}}-run-tests-fs.yml"),
    os.path.join("docs", "ml-developer-guide-fs.md"),
]

if cicd_platform in ["gitHub", "gitHubEnterprise"]:
    remove_filepath(os.path.join(".azure"))
elif cicd_platform == "azureDevOpsServices":
    remove_filepath(os.path.join(".github"))

# Remove test files
test_paths = ["_params_testing_only.txt"]
if project_name_alphanumeric_underscore != "27896cf3_bb3e_476e_8129_96df0406d5c7":
    for path in test_paths:
        os.remove(path)

# Remove MLP code in cases of Feature Store (they are not used).
if include_feature_store == "yes":
    for path in mlp_paths:
        remove_filepath(path)
# Remove Feature Store code if not selected.
else:
    for path in feature_store_paths:
        remove_filepath(path)

readme_path = os.path.join(os.getcwd(), "README.md")
print(
    f"Finished generating ML project. See the generated README at {readme_path} for next steps!"
)
