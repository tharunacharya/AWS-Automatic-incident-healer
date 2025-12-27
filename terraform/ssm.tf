resource "aws_ssm_document" "restart_service" {
  name            = "${var.project_name}-restart-service"
  document_type   = "Automation"
  document_format = "YAML"
  content         = file("${path.module}/../src/ssm_docs/restart_service.yaml")
}

resource "aws_ssm_document" "scale_up" {
  name            = "${var.project_name}-scale-up"
  document_type   = "Automation"
  document_format = "YAML"
  content         = file("${path.module}/../src/ssm_docs/scale_ec2.yaml")
}
