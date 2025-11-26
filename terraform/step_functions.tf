resource "aws_sfn_state_machine" "incident_workflow" {
  name     = "${var.project_name}-workflow"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = templatefile("${path.module}/../src/step_functions/workflow.json", {
    analyzer_arn       = aws_lambda_function.analyzer.arn
    healer_arn         = aws_lambda_function.healer.arn
    notifier_arn       = aws_lambda_function.notifier.arn
    cost_estimator_arn = aws_lambda_function.cost_estimator.arn
    approval_api_url   = "${aws_apigatewayv2_api.approval_api.api_endpoint}/approval"
  })
}


