#!/bin/bash
aws ec2 describe-regions | jq -rc '.[][].RegionName' | while read region; do echo -e "provider \"aws\" {\n  region = \"${region}\"\n  alias  = \"${region}\"\n}\n\nmodule \"${region}\" {\n  source = \"./vendor\"\n\n  providers = {\n    aws = aws.${region}\n  }\n}\n"; done > vendor.tf
