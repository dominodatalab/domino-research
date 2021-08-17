provider "aws" {
  region = "eu-north-1"
  alias  = "eu-north-1"
}

module "eu-north-1" {
  source = "./vendor"

  providers = {
    aws = aws.eu-north-1
  }
}

provider "aws" {
  region = "ap-south-1"
  alias  = "ap-south-1"
}

module "ap-south-1" {
  source = "./vendor"

  providers = {
    aws = aws.ap-south-1
  }
}

provider "aws" {
  region = "eu-west-3"
  alias  = "eu-west-3"
}

module "eu-west-3" {
  source = "./vendor"

  providers = {
    aws = aws.eu-west-3
  }
}

provider "aws" {
  region = "eu-west-2"
  alias  = "eu-west-2"
}

module "eu-west-2" {
  source = "./vendor"

  providers = {
    aws = aws.eu-west-2
  }
}

provider "aws" {
  region = "eu-west-1"
  alias  = "eu-west-1"
}

module "eu-west-1" {
  source = "./vendor"

  providers = {
    aws = aws.eu-west-1
  }
}

provider "aws" {
  region = "ap-northeast-3"
  alias  = "ap-northeast-3"
}

module "ap-northeast-3" {
  source = "./vendor"

  providers = {
    aws = aws.ap-northeast-3
  }
}

provider "aws" {
  region = "ap-northeast-2"
  alias  = "ap-northeast-2"
}

module "ap-northeast-2" {
  source = "./vendor"

  providers = {
    aws = aws.ap-northeast-2
  }
}

provider "aws" {
  region = "ap-northeast-1"
  alias  = "ap-northeast-1"
}

module "ap-northeast-1" {
  source = "./vendor"

  providers = {
    aws = aws.ap-northeast-1
  }
}

provider "aws" {
  region = "sa-east-1"
  alias  = "sa-east-1"
}

module "sa-east-1" {
  source = "./vendor"

  providers = {
    aws = aws.sa-east-1
  }
}

provider "aws" {
  region = "ca-central-1"
  alias  = "ca-central-1"
}

module "ca-central-1" {
  source = "./vendor"

  providers = {
    aws = aws.ca-central-1
  }
}

provider "aws" {
  region = "ap-southeast-1"
  alias  = "ap-southeast-1"
}

module "ap-southeast-1" {
  source = "./vendor"

  providers = {
    aws = aws.ap-southeast-1
  }
}

provider "aws" {
  region = "ap-southeast-2"
  alias  = "ap-southeast-2"
}

module "ap-southeast-2" {
  source = "./vendor"

  providers = {
    aws = aws.ap-southeast-2
  }
}

provider "aws" {
  region = "eu-central-1"
  alias  = "eu-central-1"
}

module "eu-central-1" {
  source = "./vendor"

  providers = {
    aws = aws.eu-central-1
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "us-east-1"
}

module "us-east-1" {
  source = "./vendor"

  providers = {
    aws = aws.us-east-1
  }
}

provider "aws" {
  region = "us-east-2"
  alias  = "us-east-2"
}

module "us-east-2" {
  source = "./vendor"

  providers = {
    aws = aws.us-east-2
  }
}

provider "aws" {
  region = "us-west-1"
  alias  = "us-west-1"
}

module "us-west-1" {
  source = "./vendor"

  providers = {
    aws = aws.us-west-1
  }
}

provider "aws" {
  region = "us-west-2"
  alias  = "us-west-2"
}

module "us-west-2" {
  source = "./vendor"

  providers = {
    aws = aws.us-west-2
  }
}
