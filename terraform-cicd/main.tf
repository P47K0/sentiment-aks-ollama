# =============================================
# Terraform Backend Configuration
# =============================================
provider "azurerm" {
  features {}
}

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatep47k0"
    container_name       = "tfstate"
    key                  = "sentiment-aks-ollama.tfstate"
  }
}

# =============================================
# AKS Infrastructure
# =============================================

resource "azurerm_public_ip" "traefik" {
  name                = "${var.cluster_name}-traefik-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "aks-ollama"

  default_node_pool {
    name       = "system"
    node_count = 1
    vm_size    = "Standard_D2ps_v6"     # Cheap ARM system pool
  }

  identity {
    type = "SystemAssigned"
  }
}

# Spot user nodepool for Ollama
resource "azurerm_kubernetes_cluster_node_pool" "userpool" {
  count = var.user_nodepool_enabled ? 1 : 0

  name                  = "userpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_D4s_v5"
  node_count            = 1
  mode                  = "User"

  priority        = "Spot"
  eviction_policy = "Delete"
  spot_max_price  = -1
}