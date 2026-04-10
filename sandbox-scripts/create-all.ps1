# sandbox-scripts/create-all.ps1
# > pwsh .\sandbox-scripts\create-all.ps1 -ResourceGroupName "318900_1775315728609_rg" 


param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    [string]$ClusterName = "aks-ollama-dev",
    [string]$Environment = "dev",
    [bool]$InstallTraefik = $false,
    [string]$Model = "phi3:mini"
)

Write-Host "=== Full Deployment Script ===" -ForegroundColor Cyan
Write-Host "Using Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Cluster Name        : $ClusterName" -ForegroundColor Yellow
Write-Host "Install Traefik     : $InstallTraefik" -ForegroundColor Yellow
Write-Host "Model               : $Model" -ForegroundColor Yellow

# Get the root of the project (one level above sandbox-scripts)
if ($PSScriptRoot) {
    $rootPath = Split-Path -Parent $PSScriptRoot
} else {
    $rootPath = Get-Location
}

# Fallback: if we're already in the root, use current location
if (-not (Test-Path "$rootPath/terraform")) {
    $rootPath = Get-Location
}

Write-Host "Project root detected as: $rootPath" -ForegroundColor Gray

# Change to project root
Set-Location $rootPath

Write-Host "=== Starting Full Deployment ===" -ForegroundColor Cyan

# Run Terraform
Write-Host "Running Terraform..." -ForegroundColor Yellow
Push-Location -Path "./terraform"
terraform apply -auto-approve -var="resource_group_name=$ResourceGroupName" 
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "Terraform apply failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Terraform completed successfully." -ForegroundColor Green

Write-Host "Adding B4ms user nodepool..." -ForegroundColor Yellow
az aks nodepool add `
  --resource-group $ResourceGroupName `
  --cluster-name $ClusterName `
  --name userpool `
  --node-vm-size Standard_B4ms `
  --node-count 1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to add B4ms user nodepool!" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for B4ms user nodepool to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=Ready node -l agentpool=userpool --timeout=5m

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Nodepool did not reach Ready state in time (continuing anyway)" -ForegroundColor Yellow
} else {
    Write-Host "B4ms user nodepool is Ready." -ForegroundColor Green
}

Write-Host "Running deployment script..." -ForegroundColor Yellow
.\sandbox-scripts\deploy-aks.ps1 -InstallTraefik:$InstallTraefik -ResourceGroupName $ResourceGroupName -Environment $Environment -ClusterName $ClusterName -Model $Model

Write-Host "`nFull deployment finished!" -ForegroundColor Green