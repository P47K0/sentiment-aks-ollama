variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "environment" {
  description = "Environment name (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "node_vm_size" {
  description = "VM size for AKS nodepool"
  type        = string
  default     = "Standard_D4s_v5"
}

variable "node_count" {
  description = "Number of nodes in the default nodepool"
  type        = number
  default     = 1
}