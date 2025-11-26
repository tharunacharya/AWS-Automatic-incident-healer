# Detector Lambda
data "archive_file" "detector_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/lambdas/detector"
  output_path = "${path.module}/detector.zip"
}

resource "aws_lambda_function" "detector" {
  filename         = data.archive_file.detector_zip.output_path
  function_name    = "${var.project_name}-detector"
  role             = aws_iam_role.detector_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.detector_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents.name
      STATE_MACHINE_ARN = aws_sfn_state_machine.incident_workflow.arn
    }
  }
}

# Analyzer Lambda
data "archive_file" "analyzer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/lambdas/analyzer"
  output_path = "${path.module}/analyzer.zip"
}

resource "aws_lambda_function" "analyzer" {
  filename         = data.archive_file.analyzer_zip.output_path
  function_name    = "${var.project_name}-analyzer"
  role             = aws_iam_role.analyzer_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.analyzer_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 60

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents.name
      LOGS_BUCKET = aws_s3_bucket.incident_logs.id
    }
  }
}

# Healer Lambda
data "archive_file" "healer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/lambdas/healer"
  output_path = "${path.module}/healer.zip"
}

resource "aws_lambda_function" "healer" {
  filename         = data.archive_file.healer_zip.output_path
  function_name    = "${var.project_name}-healer"
  role             = aws_iam_role.healer_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.healer_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 300

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents.name
    }
  }
}

# Notifier Lambda
data "archive_file" "notifier_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/lambdas/notifier"
  output_path = "${path.module}/notifier.zip"
}

resource "aws_lambda_function" "notifier" {
  filename         = data.archive_file.notifier_zip.output_path
  function_name    = "${var.project_name}-notifier"
  role             = aws_iam_role.notifier_role.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.notifier_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 30

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.incidents.name
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }
}

# Cost Estimator Lambda
data "archive_file" "cost_estimator_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/lambdas/cost_estimator/handler.py"
  output_path = "${path.module}/cost_estimator.zip"
}

resource "aws_lambda_function" "cost_estimator" {
  filename         = data.archive_file.cost_estimator_zip.output_path
  function_name    = "${var.project_name}-cost-estimator"
  role             = aws_iam_role.cost_estimator_role.arn
  handler          = "handler.handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.cost_estimator_zip.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}

# Approval Handler Lambda
data "archive_file" "approval_handler_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/lambdas/approval_handler/handler.py"
  output_path = "${path.module}/approval_handler.zip"
}

resource "aws_lambda_function" "approval_handler" {
  filename         = data.archive_file.approval_handler_zip.output_path
  function_name    = "${var.project_name}-approval-handler"
  role             = aws_iam_role.approval_handler_role.arn
  handler          = "handler.handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.approval_handler_zip.output_base64sha256
  timeout          = 10

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}
