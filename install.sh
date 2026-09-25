#!/bin/bash
# HackGPT shell script

# HackGPT Enterprise Installation Script
# Installs all dependencies for enterprise penetration testing platform
# Version: 2.0.0 (Production-Ready)

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

INSTALL_CONTEXT="${HACKGPT_INSTALL_CONTEXT:-host}"
case "$INSTALL_CONTEXT" in
    host)
        ROOT=(sudo)
        ;;
    container)
        ROOT=()
        ;;
    *)
        error "Unsupported HACKGPT_INSTALL_CONTEXT: $INSTALL_CONTEXT (expected host or container)"
        exit 2
        ;;
esac

run_root() {
    "${ROOT[@]}" "$@"
}

# Banner
echo -e "${PURPLE}"
echo "██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗ ██████╗ ████████╗"
echo "██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝ ██╔══██╗╚══██╔══╝"
echo "███████║███████║██║     █████╔╝ ██║  ███╗██████╔╝   ██║   "
echo "██╔══██║██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝    ██║   "
echo "██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╔╝██║        ██║   "
echo "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝        ╚═╝   "
echo -e "${NC}"
echo -e "${CYAN}Enterprise AI-Powered Penetration Testing Platform v2.0${NC}"
echo -e "${GREEN}Production-Ready | Cloud-Native | AI-Enhanced${NC}"
echo

# Update package metadata. A full host upgrade remains an explicit host-install action;
# container images should be reproducible from their declared base image instead.
echo "[+] Updating system packages..."
run_root apt-get update
if [ "$INSTALL_CONTEXT" = "host" ]; then
    run_root apt-get upgrade -y
else
    info "Container install: skipping full distribution upgrade"
fi

# Docker installs requirements in a cacheable layer before copying the source tree.
# Keep the historical host installer behavior unchanged for direct installations.
if [ "$INSTALL_CONTEXT" = "host" ]; then
    echo "[+] Installing Python dependencies..."
    pip install -r requirements.txt --break-system-packages
else
    info "Container install: Python dependencies are provided by the Docker requirements layer"
fi

# Install available pentesting tools (skip unavailable ones)
echo "[+] Installing available pentesting tools..."
run_root apt-get install -y \
    nmap \
    masscan \
    nikto \
    gobuster \
    sqlmap \
    hydra \
    whatweb \
    dnsenum \
    whois \
    netcat-traditional \
    curl \
    wget \
    git \
    john \
    hashcat \
    aircrack-ng \
    wireshark \
    tshark || warn "Some pentesting tools may not be available in repositories"

# Install additional security tools that are available
echo "[+] Installing additional security tools..."
run_root apt-get install -y \
    binwalk \
    foremost \
    steghide \
    exiftool \
    tcpdump \
    ncat \
    socat \
    proxychains4 || warn "Some additional tools may not be available"

# Local-model provisioning is a user-controlled host action. Baking a daemon and a
# multi-GB model download into the image build is non-deterministic and makes offline
# image builds impossible. The Workbench remains usable in deterministic no-AI mode.
if [ "$INSTALL_CONTEXT" = "host" ]; then
    echo "[+] Installing ollama for local AI support..."
    curl -fsSL https://ollama.ai/install.sh | sh

    echo "[+] Starting ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5

    if kill -0 "$OLLAMA_PID" 2>/dev/null; then
        echo "[+] Downloading local AI model..."
        ollama pull llama2:7b || warn "Failed to download AI model - you can do this later with 'ollama pull llama2:7b'"
    else
        warn "Ollama service failed to start - you can start it manually with 'ollama serve'"
    fi
else
    info "Container install: skipping Ollama installer, daemon start and model download"
fi

# Create reports directory
echo "[+] Creating reports directory..."
mkdir -p reports
mkdir -p logs
mkdir -p templates
mkdir -p database/migrations

# Create configuration files
echo "[+] Creating configuration files..."
if [ ! -f "config.ini" ]; then
    cat > config.ini << 'EOF'
[app]
debug = false
log_level = INFO

[database]
url = postgresql://hackgpt:hackgpt123@localhost:5432/hackgpt

[cache]
redis_url = redis://localhost:6379/0

[ai]
openai_api_key = 
local_model = llama2:7b

[security]
secret_key = 
jwt_algorithm = HS256
jwt_expiry = 3600

[features]
enable_voice = true
enable_web_dashboard = true
enable_realtime_dashboard = true
EOF
    log "Configuration file created"
fi

# Create .env template if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# HackGPT Enterprise Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://hackgpt:hackgpt123@localhost:5432/hackgpt
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
SHODAN_API_KEY=your_shodan_api_key
CENSYS_API_ID=your_censys_api_id
CENSYS_API_SECRET=your_censys_api_secret
EOF
    log "Environment template created"
fi

# Make scripts executable
chmod +x hackgpt.py hackgpt_v2.py install.sh usage_examples.sh test_installation.py
[ -f advance_hackgpt.py ] && chmod +x advance_hackgpt.py || true

# Host installs keep the historical global command. Container entrypoints are declared
# by the image itself and do not need a host-style symlink.
if [ "$INSTALL_CONTEXT" = "host" ]; then
    echo "[+] Creating global command..."
    run_root ln -sf "$(pwd)/hackgpt.py" /usr/local/bin/hackgpt || warn "Failed to create global symlink"
else
    info "Container install: using the Docker entrypoint instead of a global symlink"
fi

echo ""
echo "✅ Installation Complete!"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    INSTALLATION COMPLETE                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  1. Copy ${YELLOW}.env.example${NC} to ${YELLOW}.env${NC} and configure your API keys"
echo -e "  2. Edit ${YELLOW}config.ini${NC} to customize settings"
echo -e "  3. Run HackGPT: ${YELLOW}python3 advance_hackgpt.py${NC}"
echo ""
echo "Usage:"
echo "  ./advance_hackgpt.py             # Interactive mode"
echo "  ./advance_hackgpt.py --web       # Web dashboard"
echo "  ./advance_hackgpt.py --voice     # Voice command mode"
echo "  hackgpt                        # Global command (if symlink created)"
echo ""
echo "Set OpenAI API key (optional):"
echo "  export OPENAI_API_KEY='your-api-key-here'"
echo ""
echo -e "${GREEN}Happy Hacking! 🚀${NC}"
