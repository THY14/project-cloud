output "alb_dns_name" {
  description = "Public URL of the app"
  value       = module.alb.alb_dns_name
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.rds_endpoint
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}