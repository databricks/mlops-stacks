variable "gcp_storage_bucket_location" {
  type        = string
  description = "The Google Cloud Region where the Storage Bucket should exist (e.g 'asia-east1')."
}

variable "gcp_project_id" {
  type        = string
  description = "The Google Cloud Project ID where the Stoage Bucket will be created."
}

