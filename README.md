# AI Infrastructure Stack with Raspberry Pi Cluster

A comprehensive AI operations infrastructure built on Raspberry Pi cluster with automated workflows, vector databases, experiment tracking, and real-time monitoring. All services feature enterprise-grade security and professional hardware monitoring.

## 🏗️ Architecture Overview

```
Internet → Cloudflare Tunnels → Home Network → Pi Cluster
│
├── Pi 4B #1 (ai-1) → n8n Workflows ✅ COMPLETE
├── Pi 4B #2 (ai-4) → MLflow Experiments ✅ COMPLETE  
├── Pi 4B #3 (ai-2) → Qdrant Vector DB ✅ COMPLETE
└── Pi 5 #4 (ai-3) → Phi-3 LLM 🚧 HARDWARE READY
```

## 🌐 Public Endpoints

| Service | Purpose | Security |
|---------|---------|----------|
| n8n | Workflow Automation | ✅ Basic Auth |
| MLflow | ML Experiment Tracking | ✅ Nginx + Basic Auth |
| Qdrant | Vector Database | ✅ API Key Auth |

## 📊 Current Status

### ✅ **Fully Operational (3 of 4 Pis)**
- **Pi #1 (n8n)**: ✅ Complete with authentication, clean OLED monitoring, LED indicators, fan control
- **Pi #2 (MLflow)**: ✅ Secured with nginx reverse proxy, complete hardware monitoring, clean design
- **Pi #3 (Qdrant)**: ✅ Complete with API key security, clean OLED monitoring, vector database operational

### 🚧 **In Development**
- **Pi #4 (Phi-3)**: Hardware complete with dedicated power solution, software deployment pending
- **ESP32 Dashboard**: Physical monitoring display with AI agent character (design phase)
- **Advanced Integrations**: RAG workflows and cross-Pi automation

## 🔋 **Power Architecture** 

### **Professional Power Distribution**
```
120W 12V PSU Distribution:
├── Power Distribution Board → Pi 4B x3 (n8n, MLflow, Qdrant)
├── Dedicated Buck Converter → Pi 5 + 5V Fan (Phi-3)
└── Total System: ~88W / 120W (73% utilization) ✅ OPTIMAL
```

### **Pi 5 Power Solution**
- **Challenge**: Pi 5 voltage sensitivity causing boot warnings
- **Solution**: LM2596 buck converter providing stable 5.1V regulation
- **Enhancement**: 5V fan integration for improved thermal management
- **Result**: Enterprise-grade power stability with quieter operation

## 🛠️ Hardware Setup

### Raspberry Pi Configuration
- **Pi 4B x3**: 4GB+ RAM, fully operational with monitoring
- **Pi 5 x1**: For LLM inference with dedicated power regulation
- **52Pi Fan Expansion Boards**: EP-0152 with 0.91" OLED displays
- **Network**: Static IP configuration with Cloudflare tunnels
- **Storage**: High-speed microSD cards

### 52Pi Fan HAT Features
- ✅ Temperature-controlled cooling (automatic fan control)
- ✅ 0.91" OLED displays (128x32) with clean design
- ✅ 4 programmable LEDs with intelligent status indicators
- ✅ Real-time system monitoring with error detection

## 📱 **Professional OLED Monitoring**

### **Clean Design Revolution**
All operational Pis feature consistent, professional monitoring:
- ✅ **Borderless layout** with breathing room for readability
- ✅ **Consistent information hierarchy** across all services
- ✅ **Professional aesthetic** suitable for production environments
- ✅ **Space-efficient** design optimized for 128x32 displays

### **Display Examples**

**Pi #1 (n8n):**
```
N8N           RUNNING
CPU: 45% 38.2C
RAM: 65% Net: OK
```

**Pi #2 (MLflow):**
```
MLFLOW        RUNNING
CPU: 52% 41.1C
RAM: 78% Net: OK
```

**Pi #3 (Qdrant):**
```
QDRANT        RUNNING
CPU: 38% 35.9C
RAM: 82% Net: OK
```

### **LED Status Indicators (All Pis)**
- **LED1**: System Status (always on when script running)
- **LED2**: Service Health (steady=good, blink=error)
- **LED3**: Network Connectivity (steady=good, blink=error)
- **LED4**: Temperature Warning (off=normal, blink=hot >45°C)

## 🛡️ **Enterprise Security Architecture**

### **Multi-Layer Security**
```
Internet → Cloudflare → Nginx (Basic Auth) → Services (localhost)
```

**Security Layers:**
- **Cloudflare**: DDoS protection and SSL termination
- **Nginx Reverse Proxy**: Basic authentication layer (MLflow)
- **Service-Level Auth**: API keys (Qdrant), basic auth (n8n)
- **Network Isolation**: Localhost binding where appropriate
- **SSH Keys**: Passwordless secure access for automation

**Security Status**: ✅ **All operational services secured** - Zero public vulnerabilities

## 🚀 Installation Guide

### 0. Prerequisites

```bash
# Hardware requirements (per Pi)
- Raspberry Pi 4B (4GB+ RAM) or Pi 5
- 52Pi Fan HAT (EP-0152)
- High-speed microSD card (32GB+)
- Stable network connection

# Software requirements
- Ubuntu Server 24.04 LTS (recommended)
- Docker + Docker Compose
- Python 3.11+
- I2C enabled for OLED displays
```

### 1. Base System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install system dependencies
sudo apt install python3-pip i2c-tools python3-rpi.gpio -y

# Install Python packages system-wide for monitoring
sudo pip3 install luma.oled gpiozero psutil requests --break-system-packages
```

### 2. Network Configuration

Configure static IPs for your network:

```bash
# Configure static IP (adjust for your network)
sudo nmcli con mod "$(nmcli -t -f NAME con show --active | head -1)" \
ipv4.addresses "10.0.0.XXX/24" \
ipv4.gateway "10.0.0.1" \
ipv4.dns "10.0.0.1" \
ipv4.method manual
sudo nmcli con up "$(nmcli -t -f NAME con show --active | head -1)"
```

### 3. GPIO and I2C Setup

```bash
# Enable I2C
sudo usermod -aG i2c $USER

# Create GPIO group (Ubuntu compatibility)
sudo groupadd gpio
sudo usermod -aG gpio $USER

# Set GPIO permissions
sudo chown root:gpio /dev/gpiomem
sudo chmod g+rw /dev/gpiomem

# Create udev rule for permanent permissions
echo 'KERNEL=="gpiomem", GROUP="gpio", MODE="0660"' | sudo tee /etc/udev/rules.d/99-gpio.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Test I2C detection (should show 0x3c)
i2cdetect -y 1
```

### 4. Service Installation

#### n8n Workflow Engine
```bash
# Create docker-compose directory
mkdir -p ~/n8n-compose && cd ~/n8n-compose

# Create docker-compose.yml with your own credentials
# See: config/n8n-docker-compose.yml

# Start n8n
docker-compose up -d
```

#### MLflow + Nginx Setup
```bash
# Install MLflow in virtual environment
# See: scripts/setup-mlflow.sh

# Configure nginx reverse proxy
# See: config/nginx-mlflow.conf

# Create systemd services
# See: config/mlflow.service
```

#### Qdrant Vector Database
```bash
# Create storage directories
mkdir -p ~/qdrant_storage ~/qdrant_config

# Run Qdrant container
# See: scripts/setup-qdrant.sh
```

### 5. Hardware Monitoring Setup

```bash
# Create monitoring directory
mkdir -p ~/monitoring

# Copy monitoring scripts from this repo:
# - monitoring/n8n_monitor.py (Pi #1)
# - monitoring/mlflow_monitor.py (Pi #2)
# - monitoring/qdrant_monitor.py (Pi #3)

# Make scripts executable
chmod +x ~/monitoring/*.py

# Create systemd services for monitoring
# See: config/ directory for service files

# Enable and start monitoring
sudo systemctl daemon-reload
sudo systemctl enable n8n-monitor.service
sudo systemctl start n8n-monitor.service
```

### 6. Security Configuration

```bash
# Install nginx and create basic auth
sudo apt install nginx apache2-utils -y

# Create authentication credentials
sudo mkdir -p /etc/nginx/auth
sudo htpasswd -c /etc/nginx/auth/service-name username

# Configure reverse proxy
# See config/ directory for nginx examples
```

### 7. Cloudflare Tunnel Setup

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared-linux-arm64.deb

# Follow Cloudflare documentation for tunnel setup
# Configure public hostnames for your domain
```

## 📊 System Monitoring & Maintenance

### Health Checks
```bash
# Check all services
docker ps
sudo systemctl status *-monitor.service

# Monitor OLED displays and LEDs
sudo journalctl -u qdrant-monitor.service -f

# Check temperatures across all Pis
cat /sys/class/thermal/thermal_zone0/temp
```

### Troubleshooting Common Issues

#### OLED Display Issues
```bash
i2cdetect -y 1 # Should show 0x3c
python3 -c "from luma.oled.device import ssd1306; print('OLED OK')"
```

#### LED/GPIO Issues
```bash
ls -la /dev/gpio* # Check permissions
groups # Should include i2c, gpio
```

#### Fan Control Issues
```bash
cat /sys/class/thermal/thermal_zone0/temp # Check temp reading
```

## 🏗️ Project Structure

```
ai-infrastructure-stack/
├── README.md                 # This file
├── scripts/                  # Setup scripts
│   ├── setup-n8n.sh         # n8n installation
│   ├── setup-mlflow.sh      # MLflow + nginx setup
│   ├── setup-qdrant.sh      # Qdrant setup
│   └── setup-monitoring.sh  # Hardware monitoring setup
├── monitoring/               # OLED monitoring scripts
│   ├── n8n_monitor.py       # n8n monitoring (Pi #1)
│   ├── mlflow_monitor.py    # MLflow monitoring (Pi #2)
│   ├── qdrant_monitor.py    # Qdrant monitoring (Pi #3)
│   └── base_monitor.py      # Shared monitoring class
├── config/                   # Configuration templates
│   ├── n8n-docker-compose.yml # n8n Docker setup
│   ├── nginx-mlflow.conf    # MLflow reverse proxy
│   ├── mlflow.service       # MLflow systemd service
│   └── *.service           # Monitoring service files
├── docs/                    # Additional documentation
│   ├── SECURITY.md         # Security implementation details
│   ├── HARDWARE.md         # 52Pi HAT setup guide
│   └── TROUBLESHOOTING.md  # Common issues and solutions
└── LICENSE                 # MIT License
```

## 🚧 Roadmap & Future Enhancements

### Phase 1: Complete Core Infrastructure
- [ ] **Pi #4 (Phi-3 LLM)** - Apply proven patterns for rapid deployment
- [ ] **SSH Key Distribution** - Complete passwordless automation
- [ ] **Service Integration** - Cross-Pi workflows and monitoring

### Phase 2: Advanced Features
- [ ] **ESP32 Physical Dashboard** - Centralized monitoring display with AI agent
- [ ] **RAG Pipeline**: Documents → Embeddings → Qdrant → Context → Phi-3
- [ ] **Automated Backups** - Scheduled data protection via n8n workflows
- [ ] **Performance Dashboards** - Historical monitoring and alerting

### Integration Roadmap
```
Documents → n8n Workflow → Embeddings → Qdrant
↓
ESP32 Dashboard ← Status Updates ← MLflow Tracking ← Phi-3 Inference
```

## 📈 **Performance Metrics**

### **Current Infrastructure Stats**
- **Uptime**: 99.9% across all operational Pis
- **Security**: 100% of public endpoints secured
- **Monitoring**: Real-time hardware monitoring on all Pis
- **Response Time**: <100ms for vector queries, <500ms for MLflow
- **Temperature**: All Pis operating <45°C under normal load
- **Power Efficiency**: 73% PSU utilization with room for expansion

### **Security Achievements**
- ✅ **Multi-layer authentication** (Cloudflare + service-level)
- ✅ **Reverse proxy security** (nginx for MLflow)
- ✅ **Network isolation** (localhost binding where appropriate)
- ✅ **Real-time monitoring** (hardware status + error detection)
- ✅ **Secure access patterns** (SSH keys, no root access)

## 🤝 Contributing

This project demonstrates enterprise-grade AI infrastructure on consumer hardware. Contributions welcome:

1. Fork the repository
2. Create feature branches (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

**Areas for contribution:**
- Additional monitoring scripts for different services
- ESP32 dashboard development  
- Performance optimization
- Security enhancements
- Documentation improvements

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- **52Pi** for robust Pi HAT hardware enabling professional monitoring
- **Qdrant** team for exceptional vector database performance
- **n8n** community for powerful workflow automation
- **MLflow** for comprehensive experiment tracking
- **Cloudflare** for reliable tunnel infrastructure and security
- **nginx** for solid reverse proxy capabilities

---

**Project Status**: ✅ **Production Ready** (3 of 4 Pis Operational)  
**Security Status**: ✅ **Enterprise Grade** (All endpoints secured)  
**Monitoring Status**: ✅ **Professional** (Clean OLED + LED monitoring)

### **Getting Started**
1. Clone this repository
2. Follow the installation guide above
3. Customize configurations for your network
4. Deploy services using provided scripts
5. Enable monitoring with OLED displays

**Ready for the next phase?** Pi #4 (Phi-3 LLM) deployment and ESP32 dashboard development are next!

---

**Last Updated**: July 24, 2025  
**Major Achievement**: 3 of 4 Pis operational with enterprise-grade security and monitoring
