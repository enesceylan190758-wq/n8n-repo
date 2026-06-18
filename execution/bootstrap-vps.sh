#!/usr/bin/env bash
# Ubuntu 24.04 VPS ilk kurulum — Docker, firewall, swap
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "root olarak çalıştırın: sudo bash bootstrap-vps.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq ca-certificates curl git ufw fail2ban

# Docker (official)
if ! command -v docker >/dev/null; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    >/etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Swap (8 GB RAM altı VPS için)
if ! swapon --show | grep -q swapfile; then
  fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >>/etc/fstab
fi

# Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

systemctl enable fail2ban docker
systemctl restart fail2ban docker

mkdir -p /opt/nefalix
echo "✓ Docker $(docker --version)"
echo "✓ UFW aktif (22, 80, 443)"
echo ""
echo "Sonraki adım: repoyu /opt/nefalix altına klonlayın, .env doldurun, docker compose up"
