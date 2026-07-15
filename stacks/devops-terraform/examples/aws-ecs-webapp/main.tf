locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "vpc" {
  source = "./modules/vpc"

  project                 = var.project
  environment             = var.environment
  vpc_cidr                = var.vpc_cidr
  availability_zone_count = var.availability_zone_count
  single_nat_gateway      = var.single_nat_gateway
  tags                    = local.common_tags
}

module "alb" {
  source = "./modules/alb"

  project             = var.project
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  container_port      = var.container_port
  acm_certificate_arn = var.acm_certificate_arn
  tags                = local.common_tags
}

module "ecs_service" {
  source = "./modules/ecs-service"

  project               = var.project
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  alb_security_group_id = module.alb.alb_security_group_id
  target_group_arn      = module.alb.target_group_arn
  ecr_repository_url    = var.ecr_repository_url
  image_tag             = var.image_tag
  container_port        = var.container_port
  task_cpu              = var.task_cpu
  task_memory           = var.task_memory
  desired_count         = var.desired_count
  enable_autoscaling    = var.enable_autoscaling
  tags                  = local.common_tags

  depends_on = [module.alb]
}

module "static_site" {
  source = "./modules/static-site"

  project     = var.project
  environment = var.environment
  domain_name = var.static_site_domain
  tags        = local.common_tags
}
