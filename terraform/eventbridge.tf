resource "aws_cloudwatch_event_rule" "alarm_trigger" {
  name        = "${var.project_name}-alarm-trigger"
  description = "Trigger incident detector on CloudWatch Alarm state change"

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      state = {
        value = ["ALARM"]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "detector_target" {
  rule      = aws_cloudwatch_event_rule.alarm_trigger.name
  target_id = "DetectorLambda"
  arn       = aws_lambda_function.detector.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.detector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.alarm_trigger.arn
}
