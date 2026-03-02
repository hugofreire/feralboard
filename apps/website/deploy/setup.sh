#!/usr/bin/env bash
# Idempotent server setup for feralboard.feralbyte.com
# Installs: Node.js 20 LTS, Nginx, Certbot
# Configures: Nginx reverse-proxy with SSL for the static site
set -euo pipefail

DOMAIN="feralboard.feralbyte.com"
WEBROOT="/var/www/feralboard"
NGINX_CONF="/etc/nginx/sites-available/feralboard"
NGINX_ENABLED="/etc/nginx/sites-enabled/feralboard"
EMAIL="hugo@feralbyte.com"

echo "==> Updating package lists..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq

# ── Node.js 20 LTS ──
if command -v node &>/dev/null && node -v | grep -q "^v20"; then
  echo "==> Node.js $(node -v) already installed, skipping."
else
  echo "==> Installing Node.js 20 LTS..."
  if [ ! -f /etc/apt/keyrings/nodesource.gpg ]; then
    apt-get install -y -qq ca-certificates curl gnupg
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list
    apt-get update -qq
  fi
  apt-get install -y -qq nodejs
  echo "==> Node.js $(node -v) installed."
fi

# ── Nginx ──
if command -v nginx &>/dev/null; then
  echo "==> Nginx already installed, skipping."
else
  echo "==> Installing Nginx..."
  apt-get install -y -qq nginx
  systemctl enable nginx
  echo "==> Nginx installed."
fi

# ── Certbot ──
if command -v certbot &>/dev/null; then
  echo "==> Certbot already installed, skipping."
else
  echo "==> Installing Certbot..."
  apt-get install -y -qq certbot python3-certbot-nginx
  echo "==> Certbot installed."
fi

# ── Create webroot ──
echo "==> Ensuring webroot at ${WEBROOT}..."
mkdir -p "${WEBROOT}"

# ── Nginx config (HTTP first for certbot) ──
if [ ! -f "${NGINX_CONF}" ]; then
  echo "==> Creating Nginx config for ${DOMAIN}..."
  cat > "${NGINX_CONF}" <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};
    root ${WEBROOT};
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 256;
}
NGINX
fi

# Enable site, disable default
if [ ! -L "${NGINX_ENABLED}" ]; then
  ln -sf "${NGINX_CONF}" "${NGINX_ENABLED}"
fi
rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
nginx -t
systemctl reload nginx
echo "==> Nginx configured and reloaded."

# ── SSL via Certbot ──
if [ -d "/etc/letsencrypt/live/${DOMAIN}" ]; then
  echo "==> SSL certificate already exists for ${DOMAIN}, skipping."
else
  echo "==> Obtaining SSL certificate for ${DOMAIN}..."
  certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos -m "${EMAIL}" --redirect
  echo "==> SSL certificate obtained and Nginx configured for HTTPS."
fi

# ── Certbot auto-renewal timer ──
if systemctl is-enabled certbot.timer &>/dev/null; then
  echo "==> Certbot renewal timer already enabled."
else
  systemctl enable --now certbot.timer
  echo "==> Certbot renewal timer enabled."
fi

echo ""
echo "=========================================="
echo " Setup complete!"
echo " Domain: https://${DOMAIN}"
echo " Webroot: ${WEBROOT}"
echo "=========================================="
