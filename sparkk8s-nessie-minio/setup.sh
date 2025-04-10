#!/bin/sh
# Run this script in the terminal (./setup.sh) to prepare for deployment using Cloud Code.
echo "Updating helm"
helm repo update
if [ -z "$1" ]
  then
    echo "Changing context to docker-desktop"
    kubectl config use-context docker-desktop
  else
    echo "Using existing Kubernetes context"
fi


echo "Installing spark operator"
helm repo remove spark-operator
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

helm upgrade --install my-spark-operator spark-operator/spark-operator \
    --namespace spark-operator --create-namespace --wait
    --set webhook.enable=true

echo "Creating spark service account"
kubectl delete serviceaccount spark
kubectl create serviceaccount spark || true

echo "Setting up spark-role clusterrolebinding to spark service account"
kubectl delete clusterrolebinding spark-role
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default || true