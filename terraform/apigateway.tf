resource "aws_apigatewayv2_api" "approval_api" {
  name          = "${var.project_name}-approval-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.approval_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "approval_integration" {
  api_id           = aws_apigatewayv2_api.approval_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.approval_handler.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "approval_route_post" {
  api_id    = aws_apigatewayv2_api.approval_api.id
  route_key = "POST /approval"
  target    = "integrations/${aws_apigatewayv2_integration.approval_integration.id}"
}

resource "aws_apigatewayv2_route" "approval_route_get" {
  api_id    = aws_apigatewayv2_api.approval_api.id
  route_key = "GET /approval"
  target    = "integrations/${aws_apigatewayv2_integration.approval_integration.id}"
}

resource "aws_lambda_permission" "allow_apigateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.approval_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.approval_api.execution_arn}/*/*"
}


