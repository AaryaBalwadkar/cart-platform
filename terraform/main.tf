terraform {
  required_version = ">= 1.5.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "local" {}

resource "local_file" "cart_endpoint" {
  filename = "${path.module}/../cart_endpoint.txt"
  content  = "PORT=30093\n"
}

output "endpoint_file" {
  value = local_file.cart_endpoint.filename
}
