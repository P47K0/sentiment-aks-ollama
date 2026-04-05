# sandbox-scripts/deploy-aks.ps1
param(
    [string]$ResourceGroupName,
    [string]$Environment = "dev"      # default to dev
)

Write-Host "=== AKS Deployment Script ===" -ForegroundColor Cyan


# Get the root of the project (one level above sandbox-scripts folder)
if ($PSScriptRoot) {
    $rootPath = Split-Path -Parent $PSScriptRoot
} else {
    $rootPath = Get-Location
}

Write-Host "Project root detected as: $rootPath" -ForegroundColor Gray
Set-Location $rootPath


# Configuration
$ClusterName       = "aks-ollama-dev"
$Namespace   = $Environment

Write-Host "=== AKS Deployment Script ===" -ForegroundColor Cyan
Write-Host "Using Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Namespace      : $Namespace" -ForegroundColor Yellow

# 1. Get AKS credentials
Write-Host "Getting AKS credentials..." -ForegroundColor Yellow
az aks get-credentials --resource-group $ResourceGroupName --name $ClusterName --overwrite-existing

# Create namespace if it doesn't exist
Write-Host "Ensuring namespace '$Namespace' exists..." -ForegroundColor Yellow
kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -

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

kubectl apply -n $Namespace -f k8s/sentiment-configmap.yaml
kubectl apply -n $Namespace -f k8s/ollama-deployment.yaml
kubectl apply -n $Namespace -f k8s/llm-adapter-deployment.yaml
kubectl apply -n $Namespace -f k8s/sentiment-api-deployment.yaml

Write-Host "`n=== Deployment Completed Successfully! ===" -ForegroundColor Green
Write-Host "Namespace: $Namespace" -ForegroundColor Cyan
Write-Host "`nPublic IP Address : $publicIpAddress" -ForegroundColor Cyan
Write-Host "`nPods:" -ForegroundColor Cyan
kubectl get pods -A -n $Namespace

Write-Host "`nServices:" -ForegroundColor Cyan
kubectl get svc -A -n $Namespace

Write-Host "`nIngress:" -ForegroundColor Cyan
kubectl get ingress -A -n $Namespace

Write-Host "`nYou can monitor with: kubectl get pods -A -w" -ForegroundColor Green
Write-Host "Access your app at: http://$publicIpAddress" -ForegroundColor Cyan