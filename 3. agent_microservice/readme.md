### Steps to deploy agent micro service on eks

1. Create a fastapi wrapper to expose the agent as a service
2. Create the docker file for agent microservice for the service
3. Build the docker image and deploy the container locally to test 

```python
docker build -t agent-microservice:local .

docker run -p 8000:8000 agent-microservice:local
```

4.  Test the service

```python
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"query": "your test query"}'
```

### Push the Docker in to ECR

Build the docker image and push it in to ECR

```python
docker buildx build --platform linux/amd64 -t agent-microservice:latest . 

docker tag agent-microservice:latest {{account_id}}.dkr.ecr.us-west-2.amazonaws.com/agent-microservice:latest

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin {{account_id}}.dkr.ecr.us-west-2.amazonaws.com

docker push 924155096146.dkr.ecr.us-west-2.amazonaws.com/agent-microservice:latest
```

### Create EKS Cluster and deploy and test

1.  Create the yaml files for
    - Cluster creation
    - Deployment 
    - Service

```python
eksctl create cluster -f k8s_deploy/cluster.yaml  

./k8s_deploy/deploy-eks.sh  

curl -X POST http://a16a6c566beb64e3c839d88c29da28fa-1209057024.us-west-2.elb.amazonaws.com/agent/run -H "Content-Type: application/json" -d '{"query": "who is usain bolt"}'
```