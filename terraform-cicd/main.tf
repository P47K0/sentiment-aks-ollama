# =============================================
# Terraform Backend Configuration
# =============================================
provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}

terraform {
  backend "azurerm" {
    resource_group_name  = var.resource_group_name
    storage_account_name = var.storage_account_name
    container_name       = "tfstate"
    key                  = "sentiment-aks-ollama.tfstate"
  }
}

# =============================================
# AKS Infrastructure
# =============================================

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

resource "azurerm_kubernetes_cluster_node_pool" "userpool" {
  name                  = "userpool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks.id
  vm_size               = "Standard_D4s_v5"      # Working size
  node_count            = 1                      # One node is enough
  priority              = "Regular"              # No Spot for stability

  node_labels = {
    "agentpool" = "userpool"
  }

  tags = {
    environment = "dev"
  }
}

resource "azurerm_role_assignment" "sp_network_access" {
  scope              = azurerm_kubernetes_cluster.aks.node_resource_group_id
  role_definition_name = "Network Contributor"
  principal_id       = var.service_principal_object_id
}

resource "azurerm_public_ip" "traefik" {
  name                = "${var.cluster_name}-traefik-pip"
  location            = var.location
  resource_group_name = "MC_${var.resource_group_name}_${var.cluster_name}_${var.location}"
  allocation_method   = "Static"
  sku                 = "Standard"
  # Ensure role assignment is created before attempting to create the public IP
  depends_on = [azurerm_role_assignment.sp_network_access]
}