terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatep47k0"
    container_name       = "tfstate"
    key                  = "sentiment-aks-ollama.tfstate"
  }
}