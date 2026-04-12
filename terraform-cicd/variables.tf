variable "resource_group_name" {
  type = string
}

variable "storage_account_name" {
  default = "tfstateaz400"
}

variable "cluster_name" {
  default = "aks-ollama-dev"
}

variable "location" {
  default = "centralindia"
}

variable "user_nodepool_enabled" {
  default = true
}