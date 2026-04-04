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

- Multi-stage Azure DevOps YAML pipeline
- Infrastructure as Code with **Terraform** (AKS cluster + D4s_v5 nodepool)
- Containerized services using Docker
- Clean separation of concerns with dedicated LLM Adapter
- ConfigMap-based configuration
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
├── terraform/           # AKS cluster definition

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

## Learning Outcomes

- Modern containerized AI workload deployment on AKS
- Clean architecture patterns (Adapter pattern)
- IaC with Terraform + GitOps-style deployment
- Practical CI/CD pipeline design for multi-service applications
