output "dynamodb_table_name" {
  value = aws_dynamodb_table.incidents.name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.incident_logs.id
}

output "step_functions_arn" {
  value = aws_sfn_state_machine.incident_workflow.arn
}

output "detector_lambda_name" {
  value = aws_lambda_function.detector.function_name
}
