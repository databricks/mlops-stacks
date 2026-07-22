#!/bin/sh

# Note: we cannot assume we're running bash and use the set -euo pipefail approach.
# Usage in the wild uses the "curl | sh" approach and we need that to continue working.
set -e

VERSION="0.236.0"
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

# Known-good SHA256 checksums for the v0.236.0 release archives.
# Source: https://github.com/databricks/cli/releases/download/v0.236.0/databricks_cli_0.236.0_SHA256SUMS
checksum_for() {
    case "$1" in
    databricks_cli_0.236.0_darwin_amd64.zip) echo "9d9740eea40f89b4186c8bd9b44caacaf6a56f91d8fce7ec10cabbfec67c9ee0" ;;
    databricks_cli_0.236.0_darwin_arm64.zip) echo "fa1a945c2eaf9bc8d36d2eb7f0b394d1cfd4f4659d3de424ae7f82228ea7bd2e" ;;
    databricks_cli_0.236.0_linux_amd64.zip)  echo "4e688a4e622dceb66c109544f5b13bf4cf900e429c7b6a83d1037f3e18387fcb" ;;
    databricks_cli_0.236.0_linux_arm64.zip)  echo "7f15b96f609c9888566b5560c8c03c5f1ed20272763f28bc888ea533b8beea0c" ;;
    databricks_cli_0.236.0_windows_amd64.zip) echo "ab5a0dcd5665b787410c9cca78f1181791a5c385d53862a5fa83d03c6b10c01d" ;;
    databricks_cli_0.236.0_windows_arm64.zip) echo "a063ce7792fe31dd843a631d44a07c2f8a395f138a53e1d0e80df58c117d0310" ;;
    *) echo "" ;;
    esac
}

# Download release archive.
curl -L -s -O "https://github.com/databricks/cli/releases/download/v${VERSION}/${FILE}.zip"

# Verify the download against the known-good checksum before using it.
EXPECTED_SHA="$(checksum_for "${FILE}.zip")"
if [ -z "$EXPECTED_SHA" ]; then
    echo "No known checksum for ${FILE}.zip; refusing to proceed."
    exit 1
fi
if command -v sha256sum >/dev/null 2>&1; then
    echo "${EXPECTED_SHA}  ${FILE}.zip" | sha256sum -c - || { echo "Checksum verification failed for ${FILE}.zip"; exit 1; }
elif command -v shasum >/dev/null 2>&1; then
    echo "${EXPECTED_SHA}  ${FILE}.zip" | shasum -a 256 -c - || { echo "Checksum verification failed for ${FILE}.zip"; exit 1; }
else
    echo "No sha256sum/shasum available to verify download."
    exit 1
fi

# Unzip release archive.
unzip -q "${FILE}.zip"

# Add databricks to path.
chmod +x ./databricks
