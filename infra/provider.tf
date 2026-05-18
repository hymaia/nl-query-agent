terraform {
  required_version = ">= 1.15.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.45.0"
    }
  }

  backend "s3" {
    bucket         = "hyma-kube-terraform-state-management-dev"
    key            = "nl-query-agent/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "dev"
      project     = "nl-query-agent"
      ManagedBy   = "terraform"
    }
  }
}
