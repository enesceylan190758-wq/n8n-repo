#!/usr/bin/env bash
# npx yolunu bul (Homebrew, nvm, fnm, volta)
resolve_npx() {
  if [[ -x /opt/homebrew/bin/brew ]]; then
    # bash script'lerde .zprofile yüklenmez — Homebrew PATH'i aç
    eval "$(/opt/homebrew/bin/brew shellenv bash 2>/dev/null || /opt/homebrew/bin/brew shellenv)"
  fi

  if command -v npx >/dev/null 2>&1; then
    command -v npx
    return 0
  fi

  local candidate
  for candidate in \
    /opt/homebrew/bin/npx \
    /usr/local/bin/npx; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done

  if [[ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
    if command -v npx >/dev/null 2>&1; then
      command -v npx
      return 0
    fi
  fi

  if [[ -x "$HOME/.fnm/fnm" ]] || command -v fnm >/dev/null 2>&1; then
    eval "$(fnm env 2>/dev/null || true)"
    if command -v npx >/dev/null 2>&1; then
      command -v npx
      return 0
    fi
  fi

  if [[ -x "$HOME/.volta/bin/npx" ]]; then
    echo "$HOME/.volta/bin/npx"
    return 0
  fi

  echo "❌ npx bulunamadı. Node.js kur:" >&2
  echo "   brew install node" >&2
  echo "   veya: https://nodejs.org" >&2
  return 1
}
