# Sentiment Analysis on AKS with Self-Hosted LLM

A complete end-to-end CI/CD demonstration project built as part of my **AZ-400** preparation.

This project shows a modern DevOps workflow for deploying AI workloads on Azure Kubernetes Service (AKS).

## Architecture

The solution consists of three main components:

- **Sentiment API** – Flask-based REST API (frontend)
- **LLM Adapter** – Clean abstraction layer that converts requests to Ollama-compatible prompts
- **Ollama** – Self-hosted LLM (phi3:mini) running inside the AKS cluster

### High-level Flow
External Client → Sentiment API → LLM Adapter → Ollama (private in cluster)

## Features

- Terraform for AKS cluster + Spot user nodepool + static Public IP
- Multi-container architecture (Ollama + LLM Adapter + Flask API)
- Traefik Ingress Controller with ARM64 support
- Cost-optimized setup (Dpsv6 system pool + Spot user pool)
- ConfigMap-driven prompt for easy customization
- Proper health probes and resource limits
- Full CI/CD pipeline using Azure DevOps
- Ready for Blue-Green deployment (planned next iteration)

## Technologies Used

- **Azure Kubernetes Service (AKS)**
- **Ollama** + small LLM (phi3:mini)
- **Docker** + Docker Hub
- **Terraform** (IaC)
- **Azure DevOps** (YAML pipelines)
- **Flask** (Python)
- **KubernetesManifest** tasks

## Project Structure
sentiment-aks-ollama/

├── terraform-cicd/      # Production AKS + infrastructure

├── terraform-bootstrap/ # One-time backend storage setup

├── terraform-sb/        # Sandbox AKS + infrastructure

├── llm-adapter/         # LLM adapter service

├── sentiment-api/       # Main sentiment API

├── k8s/                 # Kubernetes manifests

├── azure-pipelines.yml  # CI/CD pipeline

└── README.md


## How to Run

1. Deploy the AKS cluster using Terraform
2. Build and push Docker images (`llm-adapter` and `sentiment-api`)
3. Apply the Kubernetes manifests from the `k8s/` folder
4. Access the sentiment API via the Ingress

**How to run in the (Whizlabs) sandbox:**
1. Log in to the Whizlabs sandbox and open Cloud Shell (PowerShell).
3. Clone the repository:
```
git clone https://github.com/P47K0/sentiment-aks-ollama.git
```
5. Init Terraform:
```
cd sentiment-aks-ollama/terraform
terraform init
cd ..
```
5. Run the full deployment script (replace with your actual resource group name)
```
pwsh ./sandbox-scripts/create-all.ps1 -ResourceGroupName "rg_sb_some_resource_group_id"
```

## Azure DevOps Pipeline (VS Pro Subscription)

The project includes a full Azure DevOps pipeline that:
- Builds and pushes Docker images to Docker Hub
- Deploys infrastructure with Terraform
- Deploys Traefik via Helm
- Deploys the application using Kubernetes manifests

See azure-pipelines.yml for details.

**One-time Setup**
Create the following service connections in your Azure DevOps project:

- **`VSPro-Azure-Connection`** – Azure Resource Manager connection to your VS Pro subscription
- **`AKS-VSPro-Connection`** – Kubernetes connection to your AKS cluster

After that, the pipeline will run automatically on every push to `main`.

> **Note:** The pipeline is configured to work across subscriptions. Make sure the service principal has Contributor rights on the target resource group.


## Technologies Used

- Infrastructure: Terraform, AKS, Spot nodepools
- Networking: Traefik Ingress, Static Public IP
- Application: Ollama, Python/Flask, Docker
- CI/CD: Azure DevOps, Docker, Helm, KubernetesManifest
- Cost Optimization: Spot instances, Dpsv6 ARM nodes
- Created NameSilo domain name with Cloudflare worker, IP for domain is updated by pipeline. When AKS is offline a static page is shown.

## Learning Outcomes

- Cost optimization strategies with Spot VMs
- Multi-nodepool AKS design
- Cross-subscription deployments
- Modern containerized AI workload deployment on AKS
- Clean architecture patterns (Adapter pattern)
- IaC with Terraform + GitOps-style deployment
- Practical CI/CD pipeline design for multi-service applications
- Real-world troubleshooting (probes, image compatibility, state management)

## TODO
- Assign Public IP created by Terraform to AKS LB.
- Use cert-manager for TLS certificates instead of Traefik‑managed certificates.
- Separate third‑party Helm deployments (Traefik, cert‑manager, etc.) from the main app deployment pipeline.


