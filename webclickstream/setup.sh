#!/bin/sh
# This script sets up the necessary components for running Apache Spark on Kubernetes
# It configures the Spark operator, service accounts, and required permissions
# Run this script in the terminal (./setup.sh) to prepare for deployment using Cloud Code.

# Update Helm repositories to ensure we have the latest charts
echo "Updating helm"
helm repo update

# Check if a Kubernetes context was provided as an argument
# If no argument is provided, use docker-desktop context
# Otherwise, use the existing context
if [ -z "$1" ]
  then
    echo "Changing context to docker-desktop"
    kubectl config use-context docker-desktop
  else
    echo "Using existing Kubernetes context"
fi

# Install the Spark Operator using Helm
# First, remove any existing spark-operator repository
# Then add the official spark-operator repository from Kubeflow
echo "Installing spark operator"
helm repo remove spark-operator
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

# Install or upgrade the Spark Operator in the spark-operator namespace
# --create-namespace: Creates the namespace if it doesn't exist
# --wait: Waits for the deployment to complete
# --set webhook.enable=true: Enables the webhook for Spark job submission
helm upgrade --install my-spark-operator spark-operator/spark-operator \
    --namespace spark-operator --create-namespace --wait \
    --set webhook.enable=true

# Create a service account for Spark jobs
# First remove any existing service account to ensure clean setup
# Then create a new service account (|| true ensures script continues if account already exists)
echo "Creating spark service account"
kubectl delete serviceaccount spark
kubectl create serviceaccount spark || true

# Set up RBAC (Role-Based Access Control) for Spark
# Create a cluster role binding that gives the spark service account edit permissions
# This allows Spark jobs to create and manage resources in the cluster
echo "Setting up spark-role clusterrolebinding to spark service account"
kubectl delete clusterrolebinding spark-role
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default || true