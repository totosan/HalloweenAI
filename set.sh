#!/bin/bash
set -e

echo "reading ENV vars from .env file"
cat .env
echo
echo export $(grep -v '^#' .env | xargs -d '\n')
