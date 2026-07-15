# ECS Service Domain Example: Networking Layer (VPC/Subnets/Routing/ALB)

This is the "data layer" this stack's ECS service depends on — the Terraform analog of the reference stack's repository layer. `modules/vpc` and `modules/alb` are applied in earlier sessions; `modules/ecs-service` consumes their outputs via `terraform_remote_state` or direct module composition.

## `modules/vpc` — Networking Foundation

```hcl
# modules/vpc/variables.tf

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR block."
  }
}

variable "availability_zone_count" {
  type        = number
  description = "Number of AZs to spread subnets across"
  default     = 2
  validation {
    condition     = var.availability_zone_count >= 2 && var.availability_zone_count <= 4
    error_message = "availability_zone_count must be between 2 and 4."
  }
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use one shared NAT gateway (cheaper, dev) instead of one per AZ (HA, prod)"
  default     = true
}
```

```hcl
# modules/vpc/main.tf

locals {
  name_prefix = "${var.project}-${var.environment}"
  azs         = slice(data.aws_availability_zones.available.names, 0, var.availability_zone_count)
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(var.tags, { Name = "${local.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = merge(var.tags, { Name = "${local.name_prefix}-igw" })
}

resource "aws_subnet" "public" {
  count                   = var.availability_zone_count
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 4, count.index)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true
  tags                     = merge(var.tags, { Name = "${local.name_prefix}-public-${local.azs[count.index]}" })
}

resource "aws_subnet" "private" {
  count             = var.availability_zone_count
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, count.index + var.availability_zone_count)
  availability_zone = local.azs[count.index]
  tags              = merge(var.tags, { Name = "${local.name_prefix}-private-${local.azs[count.index]}" })
}

resource "aws_eip" "nat" {
  count  = var.single_nat_gateway ? 1 : var.availability_zone_count
  domain = "vpc"
  tags   = merge(var.tags, { Name = "${local.name_prefix}-nat-eip-${count.index}" })
}

resource "aws_nat_gateway" "this" {
  count         = var.single_nat_gateway ? 1 : var.availability_zone_count
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  tags          = merge(var.tags, { Name = "${local.name_prefix}-nat-${count.index}" })

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(var.tags, { Name = "${local.name_prefix}-public-rt" })
}

resource "aws_route_table" "private" {
  count  = var.availability_zone_count
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.this[0].id : aws_nat_gateway.this[count.index].id
  }

  tags = merge(var.tags, { Name = "${local.name_prefix}-private-rt-${count.index}" })
}

resource "aws_route_table_association" "public" {
  count          = var.availability_zone_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = var.availability_zone_count
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
```

```hcl
# modules/vpc/outputs.tf

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.this.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets, for ALB placement"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets, for ECS task / RDS placement"
  value       = aws_subnet.private[*].id
}
```

## `modules/alb` — Load Balancer + Listener + Target Group

```hcl
# modules/alb/main.tf

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb"
  description = "Allow inbound HTTP/HTTPS from the internet"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_lb" "this" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "prod"

  tags = local.common_tags
}

resource "aws_lb_target_group" "web" {
  name        = "${local.name_prefix}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200"
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}
```

```hcl
# modules/alb/outputs.tf

output "alb_security_group_id" {
  description = "Security group ID of the ALB, consumed by modules/ecs-service to allow ingress"
  value       = aws_security_group.alb.id
}

output "target_group_arn" {
  description = "ARN of the target group, consumed by modules/ecs-service's load_balancer block"
  value       = aws_lb_target_group.web.arn
}

output "alb_dns_name" {
  description = "Public DNS name of the ALB"
  value       = aws_lb.this.dns_name
}
```

## Cross-Module Wiring (Root `main.tf`)

```hcl
module "vpc" {
  source = "./modules/vpc"

  project                 = var.project
  environment              = var.environment
  vpc_cidr                  = var.vpc_cidr
  availability_zone_count    = var.availability_zone_count
  tags                        = local.common_tags
}

module "alb" {
  source = "./modules/alb"

  project              = var.project
  environment           = var.environment
  vpc_id                 = module.vpc.vpc_id
  public_subnet_ids       = module.vpc.public_subnet_ids
  container_port           = var.container_port
  acm_certificate_arn       = var.acm_certificate_arn
  tags                        = local.common_tags
}

module "ecs_service" {
  source = "./modules/ecs-service"

  project                 = var.project
  environment              = var.environment
  aws_region                = var.aws_region
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids          = module.vpc.private_subnet_ids
  alb_security_group_id        = module.alb.alb_security_group_id
  target_group_arn              = module.alb.target_group_arn
  ecr_repository_url              = var.ecr_repository_url
  image_tag                        = var.image_tag
  tags                               = local.common_tags
}
```

This module composition (root calling `./modules/*` directly) is the pattern used within a single Terraform project. For genuinely independent lifecycles (e.g. networking owned by a platform team, deployed separately from the application), use `terraform_remote_state` data sources instead — see `vibe/vibe_state_management.md`.
