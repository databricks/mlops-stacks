#!/usr/bin/env bash
# This script generates an Azure Active Directory token for an Azure service principal,
# given the following positional command-line arguments:
# 1. Service principal tenant ID
# 2. Service principal application (client) ID
# 3. Service principal client secret
#
# It saves the token as the DATABRICKS_TOKEN environment variable for use in subsequent GitHub workflow steps.
DATABRICKS_TOKEN=$(curl --fail -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
                                              "https://login.microsoftonline.com/$1/oauth2/v2.0/token" \
                                              -d "client_id=$2" \
                                              -d 'grant_type=client_credentials' \
                                              -d 'scope=2ff814a6-3304-4ab8-85cb-cd0e6f879c1d%2F.default' \
                                              -d "client_secret=$3" |  jq -r  '.access_token')
echo "DATABRICKS_TOKEN=$DATABRICKS_TOKEN" >> "$GITHUB_ENV"
