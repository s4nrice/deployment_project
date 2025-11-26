#!/bin/bash
# Jenkins Docker Setup Script
# This script installs Docker CLI inside Jenkins container to communicate with Docker daemon

apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce-cli

# Add jenkins user to docker group
usermod -aG docker jenkins

echo "Docker CLI installed successfully"
