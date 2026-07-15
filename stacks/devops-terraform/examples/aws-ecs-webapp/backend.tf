terraform {
  backend "s3" {
    # Supplied via: terraform init -backend-config=backend.hcl
    # See backend.hcl.example for the expected keys.
  }
}
