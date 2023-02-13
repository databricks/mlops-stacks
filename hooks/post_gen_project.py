import os
import shutil


def remove_filepath(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)


root_dir = "{{cookiecutter.project_name}}"
project_name = "{{cookiecutter.project_name}}"
current_cloud = "{{cookiecutter.cloud}}"
cicd_platform = "{{cookiecutter.cicd_platform}}"
include_feature_store = "{{cookiecutter.include_feature_store}}"

mlp_paths = [
    os.path.join(project_name, "training", "profiles"),
    os.path.join(project_name, "training", "notebooks", "Train.py"),
    os.path.join(project_name, "training", "recipe.yaml"),
    os.path.join(project_name, "tests", "training", "ingest_test.py"),
    os.path.join(project_name, "tests", "training", "split_test.py"),
    os.path.join(project_name, "tests", "training", "train_test.py"),
    os.path.join(project_name, "tests", "training", "test_sample.parquet"),
    os.path.join(project_name, "tests", "training", "transform_test.py"),
    os.path.join("docs", "ml-developer-guide.md"),
]

feature_store_paths = [
    os.path.join(project_name, "feature_engineering"),
    os.path.join("tests", "feature_engineering"),
    os.path.join(project_name, "training", "notebooks", "TrainWithFeatureStore.py"),
    os.path.join(".github", "workflows", "run-tests-fs.yml"),
    os.path.join(
        "mlops-stacks-config", "terraform", "prod", "write-feature-table-job.tf"
    ),
    os.path.join(
        "mlops-stacks-config", "terraform", "staging", "write-feature-table-job.tf"
    ),
    os.path.join("docs", "ml-developer-guide-fs.md"),
]

cloud_specific_paths = {
    "azure": [
        os.path.join(".github", "workflows", "scripts", "generate-aad-token.sh"),
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "cicd", "main-azure.tf"
        ),
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "terraform", "main-azure.tf"
        ),
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "terraform", "variables.tf"
        ),
    ],
    "aws": [
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "cicd", "main-aws.tf"
        ),
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "terraform", "main-aws.tf"
        ),
    ],
}

for cloud, paths in cloud_specific_paths.items():
    if cloud != current_cloud:
        for path in paths:
            remove_filepath(path)


cicd_specific_paths = {
    "gitHub": [
        os.path.join(".github"),
    ],
    "azureDevOpsServices": [
        os.path.join(".azure"),
        os.path.join(
            "mlops-stacks-config", ".mlops-setup-scripts", "cicd", "azure-devops.tf"
        ),
    ],
}

for cicd, paths in cicd_specific_paths.items():
    if cicd != cicd_platform:
        for path in paths:
            remove_filepath(path)

# Remove test files
test_paths = ["_params_testing_only.txt"]
if project_name != "27896cf3_bb3e_476e_8129_96df0406d5c7":
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
