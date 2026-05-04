locals {
  common_tags = merge(
    {
      Environment = var.environment
      Project     = var.project
      ManagedBy   = "terraform"
      Owner       = "platform-team"
    },
    var.tags,
  )

  # Derive a single public subnet CIDR from the VPC CIDR by using the first /24 within it.
  # For a /16 VPC (e.g. 10.0.0.0/16) this produces 10.0.0.0/24.
  public_subnet_cidr = cidrsubnet(var.vpc_cidr, 8, 0)
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  # Attach the IGW to the VPC so public subnets can route to the internet.
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-igw"
  })
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidr
  map_public_ip_on_launch = true

  # Single public subnet for this minimal example.
  # For production use, replicate across availability zones using for_each.

  tags = merge(local.common_tags, {
    Name = "${var.project}-${var.environment}-public-subnet"
    Tier = "public"
  })
}
