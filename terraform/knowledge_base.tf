resource "aws_s3_bucket" "knowledge_base" {
  bucket_prefix = "${var.project_name}-kb-"
  force_destroy = true
}

resource "aws_s3_object" "runbook_5xx" {
  bucket = aws_s3_bucket.knowledge_base.id
  key    = "runbooks/5xxErrorSpike.md"
  source = "${path.module}/../src/knowledge_base/runbooks/5xxErrorSpike.md"
  etag   = filemd5("${path.module}/../src/knowledge_base/runbooks/5xxErrorSpike.md")
  content_type = "text/markdown"
}

resource "aws_s3_object" "runbook_high_cpu" {
  bucket = aws_s3_bucket.knowledge_base.id
  key    = "runbooks/HighCPU.md"
  source = "${path.module}/../src/knowledge_base/runbooks/HighCPU.md"
  etag   = filemd5("${path.module}/../src/knowledge_base/runbooks/HighCPU.md")
  content_type = "text/markdown"
}
