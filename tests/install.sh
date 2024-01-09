#!/bin/sh

# Note: we cannot assume we're running bash and use the set -euo pipefail approach.
# Usage in the wild uses the "curl | sh" approach and we need that to continue working.
set -e

VERSION="0.211.0"
FILE="databricks_cli_$VERSION"

# Include operating system in file name.
OS="$(uname -s | cut -d '-' -f 1)"
case "$OS" in
Linux)
    FILE="${FILE}_linux"
    ;;
Darwin)
    FILE="${FILE}_darwin"
    ;;
MINGW64_NT)
    FILE="${FILE}_windows"
    ;;
*)
    echo "Unknown operating system: $OS"
    exit 1
    ;;
esac

# Include architecture in file name.
ARCH="$(uname -m)"
case "$ARCH" in
i386)
    FILE="${FILE}_386"
    ;;
x86_64)
    FILE="${FILE}_amd64"
    ;;
arm)
    FILE="${FILE}_arm"
    ;;
arm64|aarch64)
    FILE="${FILE}_arm64"
    ;;
*)
    echo "Unknown architecture: $ARCH"
    exit 1
    ;;
esac

# Make sure we don't overwrite an existing installation.
if [ -f "$1/databricks" ]; then
    echo "Target path $TARGET/databricks already exists."
    exit 1
fi

# Change into test temporary directory.
cd $1

# Download release archive.
curl -L -s -O "https://github.com/databricks/cli/releases/download/v${VERSION}/${FILE}.zip"

# Unzip release archive.
unzip -q "${FILE}.zip"

# Add databricks to path.
chmod +x ./databricks
