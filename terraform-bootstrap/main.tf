# =============================================
# Terraform Backend Storage (Cool tier)
# =============================================
provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}

resource "azurerm_resource_group" "tfstate" {
  name     = "rg-terraform-state"
  location = var.location
}

resource "azurerm_storage_account" "tfstate" {
  name                     = var.storage_account_name           # must be globally unique
  resource_group_name      = azurerm_resource_group.tfstate.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  access_tier              = "Cool"
  #allow_blob_public_access = false
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}