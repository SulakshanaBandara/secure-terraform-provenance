#main.tf added
terraform {
	required_version = ">= 1.0.0"
}

provider "local"{}

resource "local_file" "example" {
	filename = "${path.module}/hello.txt"
	content = "Hellow from terraform on MacOs"
}

# malicious change

resource "local_file" "shadow" {
  content  = "touch resources not applied"
  filename = "./shadow.txt"
}

