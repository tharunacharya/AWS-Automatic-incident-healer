variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ai-incident-healer"
}

variable "slack_webhook_url" {
  description = "Slack Webhook URL for notifications"
  type        = string
}

variable "slack_signing_secret" {
  description = "Slack Signing Secret for verifying requests"
  type        = string
  default     = "" # Optional for demo
  sensitive   = true
}
