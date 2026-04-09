# ☁️ Cloud Infrastructure Project (Terraform + AWS)

## 📌 Overview

This project provisions a complete cloud infrastructure on AWS using Terraform.

Instead of manually creating resources, we use Infrastructure as Code (IaC) to automate deployment. This makes the system scalable, secure, consistent, and easy to manage.

---

## 🧠 Architecture Summary

The system includes:

- VPC (Virtual Private Cloud) – Network infrastructure
- Public & Private Subnets – Security separation
- EC2 Instances – Application servers
- Auto Scaling Group (ASG) – Automatic scaling
- Application Load Balancer (ALB) – Traffic distribution
- RDS – Managed database
- S3 – File storage
- IAM – Access control
- CloudWatch – Monitoring

---

## 🔄 System Workflow

1. User sends request to the application
2. ALB receives the request
3. ALB forwards it to EC2 instances
4. EC2 processes the request
5. Data is stored/retrieved from RDS
6. Files are stored in S3
7. CloudWatch monitors system performance

---

## 📁 Project Structure

```
project/
│── main.tf
│── variables.tf
│── outputs.tf
│── provider.tf
│── modules/
│   ├── vpc/
│   ├── s3/
│   ├── iam/
│   ├── alb/
│   ├── asg/
│   ├── rds/
│   └── cloudwatch/
```

---

## ⚙️ Prerequisites

Make sure you have:

- Terraform installed
- AWS CLI installed
- AWS account

---

## 🔧 Configuration

Configure AWS credentials:

```bash
aws configure
```

## 🚀 Deployment Steps

Initialize Terraform:

```bash
terraform init
```

Validate:

```bash
terraform validate
```

Plan:

```bash
terraform plan
```

Apply:

```bash
terraform apply
```

---

## 🧹 Destroy Resources

```bash
terraform destroy
```

---

## 🔐 Security

- Use IAM roles
- Keep database in private subnet
- Do not commit secrets
- Use environment variables or tfvars

---

## 📊 Features

- Infrastructure as Code
- Auto Scaling
- Load Balancing
- Secure architecture
- Monitoring system
- Modular design


