#!/usr/bin/env bash

set -euo pipefail

if test -d .bin; then
  echo "Directory .bin found; assuming CLI already downloaded"
  exit 0
fi

FILE="databricks_cli_$VERSION"

# Include operating system in file name.
case $AGENT_OS in
Linux)
    FILE="${FILE}_linux"
    ;;
Windows)
    FILE="${FILE}_windows"
    ;;
macOS)
    FILE="${FILE}_darwin"
    ;;
esac

# Include architecture in file name.
case $AGENT_ARCHITECTURE in
X86)
    FILE="${FILE}_386"
;;
X64)
    FILE="${FILE}_amd64"
;;
ARM)
    FILE="${FILE}_arm"
;;
ARM64)
    FILE="${FILE}_arm64"
;;
esac

# Download release archive.
curl -s -O "https://databricks-bricks.s3.amazonaws.com/v${VERSION}/${FILE}.zip"

# Unzip release archive.
unzip -q "${FILE}.zip" -d .bin

# Add databricks to path.
dir=$PWD/.bin
chmod +x "${dir}/databricks"
echo "Adding Databricks CLI to the PATH: ${dir}"
echo "##vso[task.prependpath]${dir}"