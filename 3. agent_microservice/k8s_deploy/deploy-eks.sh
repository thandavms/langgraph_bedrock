#!/bin/bash
set -e

# Configuration
CLUSTER_NAME="langgraph-cluster"
REGION="us-west-2"  # Using your region
NAMESPACE="langgraph-agent"

# Get ECR repository URI from the ECS deployment
ECR_REPOSITORY_URI=$(aws ecr describe-repositories --repository-names agent-microservice --region $REGION --query 'repositories[0].repositoryUri' --output text 2>/dev/null || echo "")

if [ -z "$ECR_REPOSITORY_URI" ]; then
    echo "Error: Could not find ECR repository. Please make sure it exists."
    echo "If your repository has a different name, please update this script."
    exit 1
fi

echo "Using ECR repository: $ECR_REPOSITORY_URI"

# Update kubeconfig for the EKS cluster
echo "Updating kubeconfig for cluster $CLUSTER_NAME..."
aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION

# Create namespace if it doesn't exist
kubectl get namespace $NAMESPACE >/dev/null 2>&1 || kubectl create namespace $NAMESPACE
echo "Using namespace: $NAMESPACE"

# Create deployment manifest
cat > k8s_deploy/deployment-updated.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-agent
  labels:
    app: langgraph-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: langgraph-agent
  template:
    metadata:
      labels:
        app: langgraph-agent
    spec:
      containers:
      - name: langgraph-agent
        image: ${ECR_REPOSITORY_URI}:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

# Create service manifest
cat > k8s_deploy/service-updated.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: langgraph-agent-service
spec:
  selector:
    app: langgraph-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
EOF

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s_deploy/deployment-updated.yaml -n $NAMESPACE
kubectl apply -f k8s_deploy/service-updated.yaml -n $NAMESPACE

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/langgraph-agent -n $NAMESPACE

# Get service URL
echo "Getting service URL..."
EXTERNAL_IP=""
while [ -z $EXTERNAL_IP ]; do
  echo "Waiting for external IP..."
  EXTERNAL_IP=$(kubectl get service langgraph-agent-service -n $NAMESPACE --output jsonpath='{.status.loadBalancer.ingress[0].hostname}')
  if [ -z "$EXTERNAL_IP" ]; then
    EXTERNAL_IP=$(kubectl get service langgraph-agent-service -n $NAMESPACE --output jsonpath='{.status.loadBalancer.ingress[0].ip}')
  fi
  [ -z "$EXTERNAL_IP" ] && sleep 10
done

echo "====================================================="
echo "🚀 LangGraph Agent deployed successfully!"
echo "📊 Service URL: http://$EXTERNAL_IP"
echo "====================================================="
echo "Test your API with:"
echo "curl -X POST http://$EXTERNAL_IP/agent/run -H \"Content-Type: application/json\" -d '{\"query\": \"your test query\"}'"
echo "====================================================="
