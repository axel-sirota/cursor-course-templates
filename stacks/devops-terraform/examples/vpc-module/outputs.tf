output "vpc_id" {
  description = "ID of the VPC. Reference this in other modules instead of hardcoding the VPC ID."
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "ID of the public subnet. Use this when launching resources that require a subnet ID."
  value       = aws_subnet.public.id
}

output "internet_gateway_id" {
  description = "ID of the internet gateway attached to the VPC. Useful for route table associations."
  value       = aws_internet_gateway.main.id
}
