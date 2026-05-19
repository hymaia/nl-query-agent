variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "nl-query-agent"
}

variable "data_platform_role_name" {
  description = "Nom du role IAM géré par la data platform"
  type        = string
  default     = "hyma-mds-nl-query-agent-role"
}

variable "athena_workgroup" {
  description = "Existing Athena workgroup name"
  type        = string
  default     = "hymaia-datalake-agent-workgroup"
}

variable "github_org" {
  description = "GitHub organization or user"
  type        = string
  default     = "hymaia"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "nl-query-agent"
}

variable "glue_database" {
  description = "Glue database name"
  type        = string
  default     = "hymaia_datalake_raw"
}

variable "athena_output_bucket" {
  description = "S3 URI used by Athena for query results"
  type        = string
  default     = "s3://raw-athena-results/output"
}

variable "bedrock_model_id" {
  description = "Bedrock model ID"
  type        = string
  default     = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
}
