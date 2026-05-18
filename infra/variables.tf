variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "nl-sql-agent"
}

variable "data_platform_role_name" {
  description = "Nom du role IAM géré par la data platform"
  type        = string
}

variable "athena_workgroup" {
  description = "Existing Athena workgroup name"
  type        = string
  default     = "primary"
}

variable "github_org" {
  description = "GitHub organization or user"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "nl-sql-agent"
}

variable "glue_database" {
  description = "Glue database name"
  type        = string
}

variable "athena_output_bucket" {
  description = "S3 URI used by Athena for query results"
  type        = string
}

variable "ingress_host" {
  description = "Hostname exposé par l'ingress ALB"
  type        = string
}

variable "certificate_arn" {
  description = "ARN du certificat ACM pour l'ingress ALB"
  type        = string
}

variable "bedrock_model_id" {
  description = "Bedrock model ID"
  type        = string
  default     = "anthropic.claude-sonnet-4-5"
}
