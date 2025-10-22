

# Spigot updater


## Installation & setup

Visit [the docs](https://left4craft.github.io/spigot-updater/) for installation, setup, and configuration instructions.

### Quick Start (Python)

**Prerequisites**: Python 3.12+ or Docker

**Local Installation**:

```bash
# Clone the repository
git clone https://github.com/astr0n8t/spigot-updater.git
cd spigot-updater

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for SpigotMC scraping)
playwright install chromium

# Configure
cp example.env .env
# Edit .env with your Discord token and other settings

cp config/example-config.yaml config/config.yaml
cp config/example-servers.yaml config/servers.yaml  
cp config/example-plugins.yaml config/plugins.yaml
# Edit config files for your setup

# Run
python -m src
```

### Docker Installation

This project now includes Docker support for easy deployment:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/astr0n8t/spigot-updater.git
   cd spigot-updater
   ```

2. **Copy and configure environment**:
   ```bash
   cp example.env .env
   # Edit .env with your Discord token and other settings
   ```

3. **Configure your servers and plugins**:
   ```bash
   # Copy and modify the example config files
   cp config/example-config.yaml config/config.yaml
   cp config/example-servers.yaml config/servers.yaml
   cp config/example-plugins.yaml config/plugins.yaml
   ```

4. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

The Docker image includes all necessary dependencies including Chromium for Playwright web scraping.

