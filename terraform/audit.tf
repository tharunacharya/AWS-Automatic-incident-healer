resource "aws_dynamodb_table" "audit_log" {
  name           = "${var.project_name}-audit"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "IncidentID"
  range_key      = "Timestamp"

  attribute {
    name = "IncidentID"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  tags = {
    Name        = "${var.project_name}-audit"
    Environment = "Production"
    Compliance  = "ImmutableLedger"
  }
}
