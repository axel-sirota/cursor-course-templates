output "bucket_name" {
  description = "Name of the S3 bucket holding static assets"
  value       = aws_s3_bucket.assets.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.assets.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.assets.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID, used for cache invalidation in deploy scripts"
  value       = aws_cloudfront_distribution.assets.id
}
