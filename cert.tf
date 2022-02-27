# ### SSL ###
# resource "google_compute_managed_ssl_certificate" "cloudrun" {
#   name = "cloudrun"
#   managed {
#     domains = ["pacjent.dimedic.eu."]
#   }
# }
#
# resource "google_compute_ssl_policy" "prod-ssl-policy" {
#   name            = "ssl-policy"
#   profile         = "MODERN"
#   min_tls_version = "TLS_1_2"
# }
