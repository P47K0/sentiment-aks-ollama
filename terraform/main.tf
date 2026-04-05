terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}

  # Required for Whizlabs sandbox - prevents permission errors
  resource_provider_registrations = "none"
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Static Public IP for Traefik Load Balancer
resource "azurerm_public_ip" "traefik_ip" {
  name                = "traefik-public-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = "sentiment-demo"   # optional: creates a DNS name
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-ollama-${var.environment}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "aks-ollama-${var.environment}"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_vm_size
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Project     = "ollama-aks-demo"
  }
}