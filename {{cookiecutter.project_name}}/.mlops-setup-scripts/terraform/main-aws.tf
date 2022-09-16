// Note: AWS region must be specified via environment variable or via the `region` field
// in the provider block below, as described
// in https://registry.terraform.io/providers/hashicorp/aws/latest/docs#environment-variables
provider "aws" {
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "{{cookiecutter.project_name}}-tfstate"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "{{cookiecutter.project_name}}-tfstate-lock"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

// Define IAM policy with appropriate permissions on S3 bucket and Dynamo DB table,
// as described in https://www.terraform.io/language/settings/backends/s3#credentials-and-shared-configuration
data "aws_iam_policy_document" "terraform_manage_state_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]

    resources = [
      "${aws_s3_bucket.terraform_state.arn}/*",
      "${aws_s3_bucket.terraform_state.arn}",
      "${aws_dynamodb_table.terraform_state_lock.arn}",
    ]
  }
}

resource "aws_iam_policy" "my-s3-read-policy" {
  name        = "{{cookiecutter.project_name}}-terraform-state-manage"
  description = "S3 bucket access policy for managing terraform state for {{cookiecutter.project_name}}"
  policy      = data.aws_iam_policy_document.terraform_manage_state_policy.json
}


resource "aws_iam_user_policy_attachment" "test-attach" {
  user       = aws_iam_user.s3_bucket_cicd_user.name
  policy_arn = aws_iam_policy.my-s3-read-policy.arn
}

// Create an IAM user with permissions to access the created S3 bucket
resource "aws_iam_user" "s3_bucket_cicd_user" {
  name = "{{cookiecutter.project_name}}-terraform-cicd-user"
}

resource "aws_iam_access_key" "s3_bucket_cicd_key" {
  user = aws_iam_user.s3_bucket_cicd_user.name
}

// Create a second S3 bucket and DynamoDB table for storing terraform state for CI/CD
// service principals
resource "aws_s3_bucket" "cicd_terraform_state" {
  bucket = "{{cookiecutter.project_name}}-cicd-setup-tfstate"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "cicd_terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "cicd_terraform_state_lock" {
  name           = "{{cookiecutter.project_name}}-cicd-setup-tfstate-lock"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

output "AWS_ACCESS_KEY_ID" {
  value = aws_iam_access_key.s3_bucket_cicd_key.id
}

output "AWS_SECRET_ACCESS_KEY" {
  value     = aws_iam_access_key.s3_bucket_cicd_key.secret
  sensitive = true
}
