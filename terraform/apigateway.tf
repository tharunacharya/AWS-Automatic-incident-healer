resource "aws_apigatewayv2_api" "approval_api" {
  name          = "${var.project_name}-approval-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_authorizer" "cognito_auth" {
  api_id           = aws_apigatewayv2_api.approval_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.client.id]
    issuer   = "https://${aws_cognito_user_pool.pool.endpoint}"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.approval_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_route" "slack_actions_route" {
  api_id    = aws_apigatewayv2_api.approval_api.id
  route_key = "POST /slack/actions"
  target    = "integrations/${aws_apigatewayv2_integration.slack_action_integration.id}"
}

resource "aws_apigatewayv2_route" "frontend_approval_get" {
  api_id    = aws_apigatewayv2_api.approval_api.id
  route_key = "GET /approval/{approvalId}"
  target    = "integrations/${aws_apigatewayv2_integration.frontend_approval_integration.id}"
}

resource "aws_apigatewayv2_route" "frontend_approval_decision" {
  api_id    = aws_apigatewayv2_api.approval_api.id
  route_key = "POST /approval/{approvalId}/decision"
  target    = "integrations/${aws_apigatewayv2_integration.frontend_approval_integration.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito_auth.id
}

resource "aws_apigatewayv2_integration" "slack_action_integration" {
  api_id           = aws_apigatewayv2_api.approval_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.slack_action_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "frontend_approval_integration" {
  api_id           = aws_apigatewayv2_api.approval_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.frontend_approval_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_apigateway_slack" {
  statement_id  = "AllowExecutionFromAPIGatewaySlack"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slack_action_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.approval_api.execution_arn}/*/*/slack/actions"
}

resource "aws_lambda_permission" "allow_apigateway_frontend" {
  statement_id  = "AllowExecutionFromAPIGatewayFrontend"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.frontend_approval_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.approval_api.execution_arn}/*/*/approval/*"
}


