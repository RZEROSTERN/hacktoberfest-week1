#!/usr/bin/env bash
# Sets up Gemma 4 on a DigitalOcean GPU Droplet (AI/ML-ready Ubuntu image, NVIDIA drivers
# preinstalled). Ollama listens on localhost only; Caddy serves it over HTTPS and rejects
# any request without the bearer token.
#
# Usage (as root on the droplet):  OLLAMA_TOKEN=<long random string> bash setup.sh
set -euo pipefail

: "${OLLAMA_TOKEN:?Set OLLAMA_TOKEN to a long random string (e.g. openssl rand -hex 32)}"
MODEL="${MODEL:-gemma4:e4b}"
PUBLIC_IP="$(curl -fsS http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)"
DOMAIN="${DOMAIN:-${PUBLIC_IP//./-}.sslip.io}" # free hostname that resolves to the IP

echo "==> GPU check"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

echo "==> Installing Ollama (https://docs.ollama.com/linux)"
curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf <<CONF
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_KEEP_ALIVE=24h"
CONF
systemctl daemon-reload
systemctl restart ollama
until curl -fsS http://127.0.0.1:11434/api/version >/dev/null; do sleep 1; done
ollama pull "$MODEL"

echo "==> Installing Caddy (https://caddyserver.com/docs/install)"
apt install --yes debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
chmod o+r /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install --yes caddy

cat > /etc/caddy/Caddyfile <<CADDY
${DOMAIN} {
	@authorized header Authorization "Bearer ${OLLAMA_TOKEN}"
	handle @authorized {
		reverse_proxy 127.0.0.1:11434 {
			header_up Host localhost:11434
		}
	}
	respond "Unauthorized" 401
}
CADDY
chmod 640 /etc/caddy/Caddyfile
chown root:caddy /etc/caddy/Caddyfile
systemctl reload caddy

if command -v ufw >/dev/null; then
  ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
fi

echo
echo "Done. Set these on the Render service paperwork-api:"
echo "  OLLAMA_BASE_URL=https://${DOMAIN}"
echo "  OLLAMA_API_KEY=<the OLLAMA_TOKEN you used>"
echo "Check:  curl -H 'Authorization: Bearer \$OLLAMA_TOKEN' https://${DOMAIN}/api/version"
