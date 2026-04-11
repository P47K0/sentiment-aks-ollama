variable "location" {
  description = "Azure region"
  type        = string
  default     = "westus"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "resource_group_name" {
  description = "Name of the resource group (from sandbox)"
  type        = string
}

variable "node_vm_size" {
  description = "VM size for AKS nodepool"
  type        = string
  default     = "Standard_D2as_v4"
}

variable "node_count" {
  description = "Number of nodes in the default nodepool"
  type        = number
  default     = 1
}