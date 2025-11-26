resource "aws_cognito_user_pool" "pool" {
  name = "${var.project_name}-user-pool"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  username_attributes = ["email"]
  auto_verified_attributes = ["email"]

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject = "Account Confirmation"
    email_message = "Your confirmation code is {####}"
  }
  
  tags = {
    Project = var.project_name
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name = "${var.project_name}-frontend-client"

  user_pool_id = aws_cognito_user_pool.pool.id

  generate_secret     = false
  explicit_auth_flows = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_PASSWORD_AUTH"]
  
  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_user_pool_domain" "domain" {
  domain       = "${var.project_name}-auth-${random_string.suffix.result}"
  user_pool_id = aws_cognito_user_pool.pool.id
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.pool.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.client.id
}

output "cognito_domain" {
  value = aws_cognito_user_pool_domain.domain.domain
}
