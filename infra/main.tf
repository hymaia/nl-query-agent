data "aws_caller_identity" "current" {}

# ==============================================================
# ECR
# ==============================================================
resource "aws_ecr_repository" "app" {
  name                 = var.app_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    App = var.app_name
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Garder les 10 dernières images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ==============================================================
# Bedrock
# Note : l'activation du modèle Anthropic Claude Sonnet se fait
# manuellement dans la console AWS Bedrock → Model access,
# ou via AWS CLI :
# aws bedrock put-foundation-model-entitlement \
#   --model-id anthropic.claude-sonnet-4-5 \
#   --region eu-west-1
# ==============================================================

# ==============================================================
# Athena — récupération du workgroup existant
# ==============================================================
data "aws_athena_workgroup" "existing" {
  name = var.athena_workgroup
}

# ==============================================================
# IAM Role Pod — géré par la data platform
# ==============================================================
data "aws_iam_role" "pod" {
  name = var.data_platform_role_name
}

data "aws_iam_policy_document" "pod_permissions" {
  statement {
    effect    = "Allow"
    actions   = ["bedrock:InvokeModel"]
    resources = ["arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-sonnet-4-5"]
  }
}

resource "aws_iam_policy" "pod" {
  name   = "${var.app_name}-pod-policy"
  policy = data.aws_iam_policy_document.pod_permissions.json
}

resource "aws_iam_role_policy_attachment" "pod" {
  role       = data.aws_iam_role.pod.name
  policy_arn = aws_iam_policy.pod.arn
}

# ==============================================================
# IAM Role — GitHub Actions (OIDC)
# ==============================================================
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.app_name}-github-actions-role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json

  tags = {
    App = var.app_name
  }
}

data "aws_iam_policy_document" "github_actions_permissions" {
  statement {
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:BatchGetImage",
    ]
    resources = [aws_ecr_repository.app.arn]
  }
}

resource "aws_iam_policy" "github_actions" {
  name   = "${var.app_name}-github-actions-policy"
  policy = data.aws_iam_policy_document.github_actions_permissions.json
}

resource "aws_iam_role_policy_attachment" "github_actions" {
  role       = aws_iam_role.github_actions.name
  policy_arn = aws_iam_policy.github_actions.arn
}

resource "local_file" "values" {
  content = templatefile("${path.module}/templates/values.yaml.tpl", {
    ecr_repository_url   = aws_ecr_repository.app.repository_url
    pod_iam_role_arn     = data.aws_iam_role.pod.arn
    aws_region           = var.aws_region
    bedrock_model_id     = var.bedrock_model_id
    glue_database        = var.glue_database
    athena_output_bucket = var.athena_output_bucket
    athena_workgroup     = var.athena_workgroup
    ingress_host         = var.ingress_host
    certificate_arn      = var.certificate_arn
  })
  filename = "${path.module}/../helm/values.yaml"
}
