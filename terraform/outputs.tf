output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "public_ip_address" {
  value = azurerm_public_ip.traefik_ip.ip_address
}

output "public_ip_name" {
  value = azurerm_public_ip.traefik_ip.name
}

output "aks_host" {
  value = azurerm_kubernetes_cluster.aks.kube_config[0].host
}

output "aks_kubeconfig" {
  value       = azurerm_kubernetes_cluster.aks.kube_config_raw
  sensitive   = true
}