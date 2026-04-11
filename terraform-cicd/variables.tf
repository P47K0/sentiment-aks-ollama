variable "resource_group_name" {
  type = string
}

variable "cluster_name" {
  default = "aks-ollama-dev"
}

variable "location" {
  default = "westeurope"
}

variable "user_nodepool_enabled" {
  default = true
}