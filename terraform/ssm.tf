resource "aws_ssm_document" "restart_service" {
  name          = "${var.project_name}-restart-service"
  document_type = "Automation"
  document_format = "YAML"
  content       = file("${path.module}/../src/ssm_docs/restart_service.yaml")
}
