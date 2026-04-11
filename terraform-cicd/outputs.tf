output "traefik_public_ip" {
  value = azurerm_public_ip.traefik.ip_address
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}