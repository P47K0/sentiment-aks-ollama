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

  # Required for Whizlabs sandbox
  resource_provider_registrations = "none"
}

# Use the existing sandbox resource group (do NOT create a new one)
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# Static Public IP for Traefik Load Balancer
resource "azurerm_public_ip" "traefik_ip" {
  name                = "traefik-public-ip"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "aks-ollama-dev"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = "aks-ollama-dev"

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