#!/bin/bash
set -e

echo "Deploying AI Incident Healer..."

# Check for required tools
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it first."
    exit 1
fi

# Initialize Terraform
cd terraform
terraform init

# Plan
echo "Planning deployment..."
terraform plan -out=tfplan

# Apply
read -p "Do you want to apply this plan? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply tfplan
else
    echo "Deployment cancelled."
fi
