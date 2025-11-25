resource "aws_s3_bucket" "incident_logs" {
  bucket_prefix = "${var.project_name}-logs-"
  force_destroy = true

  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "incident_logs" {
  bucket = aws_s3_bucket.incident_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "incident_logs" {
  bucket = aws_s3_bucket.incident_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
