resource "aws_dynamodb_table" "incidents" {
  name           = "${var.project_name}-incidents"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "incident_id"
  range_key      = "timestamp"

  attribute {
    name = "incident_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  tags = {
    Project = var.project_name
  }
}

resource "aws_dynamodb_table" "approvals" {
  name           = "${var.project_name}-approvals"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "approval_id"

  attribute {
    name = "approval_id"
    type = "S"
  }
  
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Project = var.project_name
  }
}
