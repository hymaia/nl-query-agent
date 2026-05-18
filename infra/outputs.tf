output "ecr_repository_url" {
  description = "URL du repository ECR — à renseigner dans image.repository du values.yaml"
  value       = aws_ecr_repository.app.repository_url
}

output "pod_iam_role_arn" {
  description = "ARN du role IAM à renseigner dans values.yaml (serviceAccount.iamRoleArn)"
  value       = data.aws_iam_role.pod.arn
}

output "github_actions_role_arn" {
  description = "ARN du role IAM à renseigner dans le GitHub Actions (role-to-assume)"
  value       = aws_iam_role.github_actions.arn
}
