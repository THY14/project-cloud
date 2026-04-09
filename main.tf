module "vpc" {
  source               = "./modules/vpc"
  project_name         = var.project_name
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
}

module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
}

module "iam" {
  source       = "./modules/iam"
  project_name = var.project_name
  s3_bucket_arn = module.s3.bucket_arn
}

module "alb" {
  source            = "./modules/alb"
  project_name      = var.project_name
  public_subnet_ids = module.vpc.public_subnet_ids
  vpc_id            = module.vpc.vpc_id
}

module "asg" {
  source              = "./modules/asg"
  project_name        = var.project_name
  instance_type       = var.instance_type
  public_subnet_ids   = module.vpc.public_subnet_ids
  vpc_id              = module.vpc.vpc_id
  target_group_arn    = module.alb.target_group_arn
  iam_instance_profile = module.iam.instance_profile_name
  security_group_id   = module.alb.ec2_sg_id
}

module "rds" {
  source             = "./modules/rds"
  project_name       = var.project_name
  private_subnet_ids = module.vpc.private_subnet_ids
  vpc_id             = module.vpc.vpc_id
  db_username        = var.db_username
  db_password        = var.db_password
  db_name            = var.db_name
}

module "cloudwatch" {
  source       = "./modules/cloudwatch"
  project_name = var.project_name
  asg_name     = module.asg.asg_name
}