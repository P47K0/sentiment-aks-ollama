# sandbox-scripts/deploy-aks.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    [string]$ClusterName = "aks-ollama-dev",
    [string]$Environment = "dev",
    [bool]$InstallTraefik = $false
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
$Namespace   = $Environment

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

if ($InstallTraefik) {
    $publicIpAddress = terraform -chdir=terraform output -raw public_ip_address
    if (-not $publicIpAddress) {
        Write-Host "ERROR: Could not read Public IP from Terraform." -ForegroundColor Red
        exit 1
    }
    Write-Host "Using static Public IP: $publicIpAddress" -ForegroundColor Green
}

# 3. Install Traefik Ingress Controller with static IP
if ($InstallTraefik) {
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
} else {
    Write-Host "Skipping Traefik installation (sandbox mode)" -ForegroundColor Yellow
}

# 4. Apply all application manifests
Write-Host "Applying application manifests..." -ForegroundColor Yellow

kubectl apply -n $Namespace -f k8s/sentiment-configmap.yaml
kubectl apply -n $Namespace -f k8s/ollama-deployment.yaml
kubectl apply -n $Namespace -f k8s/llm-adapter-deployment.yaml
kubectl apply -n $Namespace -f k8s/sentiment-api-deployment.yaml
if ($InstallTraefik) {
    kubectl apply -n $Namespace -f k8s/sentiment-api-ingress.yaml
    Write-Host "Ingress applied." -ForegroundColor Green
} else {
    Write-Host "Skipping Ingress (sandbox mode)" -ForegroundColor Yellow
}

Write-Host "Waiting for Ollama pod to be ready (max 5 minutes)..." -ForegroundColor Yellow
if (kubectl wait --for=condition=ready pod -l app=ollama -n $Namespace --timeout=5m) {
    Write-Host "Ollama pod is ready." -ForegroundColor Green
    
    # Pull the model only if Ollama is ready
    Write-Host "Pulling model '$Model'..." -ForegroundColor Yellow
    kubectl exec -it deploy/ollama -n $Namespace -- ollama pull $Model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Model pulled successfully." -ForegroundColor Green
    } else {
        Write-Host "Warning: Model pull failed. It will pull on first use." -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: Ollama pod did not become ready in time. Skipping model pull." -ForegroundColor Yellow
    Write-Host "Ollama will pull the model automatically on first request." -ForegroundColor Yellow
}

Write-Host "`n=== Deployment Completed Successfully! ===" -ForegroundColor Green
Write-Host "Namespace: $Namespace" -ForegroundColor Cyan

if ($InstallTraefik) {
    Write-Host "Public IP: $publicIpAddress" -ForegroundColor Cyan
}

Write-Host "`nPods:" -ForegroundColor Cyan
kubectl get pods -A -n $Namespace

Write-Host "`nServices:" -ForegroundColor Cyan
kubectl get svc -A -n $Namespace

Write-Host "`nIngress:" -ForegroundColor Cyan
kubectl get ingress -A -n $Namespace

Write-Host "`nYou can monitor with: kubectl get pods -A -w" -ForegroundColor Green
Write-Host "Access your app at: http://$publicIpAddress" -ForegroundColor Cyan