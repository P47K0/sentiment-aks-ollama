# sandbox-scripts/deploy-aks.ps1
# Deployment script - reads Public IP from Terraform and deploys all services

# Get the root of the project (one level above sandbox-scripts folder)
if ($PSScriptRoot) {
    $rootPath = Split-Path -Parent $PSScriptRoot
} else {
    $rootPath = Get-Location
}

Write-Host "Project root detected as: $rootPath" -ForegroundColor Gray
Set-Location $rootPath

Write-Host "=== AKS Deployment Script ===" -ForegroundColor Cyan

# Configuration
$ResourceGroupName = "rg-ollama-dev"
$ClusterName       = "aks-ollama-dev"

# 1. Get AKS credentials
Write-Host "Getting AKS credentials..." -ForegroundColor Yellow
az aks get-credentials --resource-group $ResourceGroupName --name $ClusterName --overwrite-existing

# 2. Read the static Public IP from Terraform output
Write-Host "Reading Public IP from Terraform output..." -ForegroundColor Yellow

$publicIpAddress = terraform -chdir=terraform output -raw public_ip_address

if (-not $publicIpAddress) {
    Write-Host "ERROR: Could not read Public IP from Terraform output." -ForegroundColor Red
    Write-Host "Make sure you have run Terraform first and that outputs.tf contains 'public_ip_address'" -ForegroundColor Red
    exit 1
}

Write-Host "Using static Public IP: $publicIpAddress" -ForegroundColor Green

# 3. Install Traefik Ingress Controller with static IP
Write-Host "Installing Traefik Ingress Controller..." -ForegroundColor Yellow

helm repo add traefik https://helm.traefik.io/traefik
helm repo update

helm upgrade --install traefik traefik/traefik `
  --namespace ingress `
  --create-namespace `
  --set service.type=LoadBalancer `
  --set service.spec.loadBalancerIP=$publicIpAddress `
  --set service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"=$ResourceGroupName

Write-Host "Traefik installed successfully!" -ForegroundColor Green

# 4. Apply all application manifests
Write-Host "Applying application manifests..." -ForegroundColor Yellow

kubectl apply -f k8s/sentiment-configmap.yaml
kubectl apply -f k8s/ollama-deployment.yaml
kubectl apply -f k8s/llm-adapter-deployment.yaml
kubectl apply -f k8s/sentiment-api-deployment.yaml
kubectl apply -f k8s/sentiment-api-service.yaml
kubectl apply -f k8s/ingress.yaml

Write-Host "`n=== Deployment Completed Successfully! ===" -ForegroundColor Green

# Final status
Write-Host "`nPublic IP Address : $publicIpAddress" -ForegroundColor Cyan
Write-Host "`nPods:" -ForegroundColor Cyan
kubectl get pods -A

Write-Host "`nServices:" -ForegroundColor Cyan
kubectl get svc -A

Write-Host "`nIngress:" -ForegroundColor Cyan
kubectl get ingress -A

Write-Host "`nYou can monitor with: kubectl get pods -A -w" -ForegroundColor Green
Write-Host "Access your app at: http://$publicIpAddress" -ForegroundColor Cyan