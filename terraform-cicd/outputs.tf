#output "aks_public_ip" {
#  value = azurerm_public_ip.traefik.ip_address
#}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

#output "aks_pip_name" {
#  value = azurerm_public_ip.traefik.name
#}

#output "aks_pip_rg_name" {
#  value = azurerm_public_ip.traefik.resource_group_name
#}
