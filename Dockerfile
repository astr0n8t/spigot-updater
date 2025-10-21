# Use Python 3.12 slim image
FROM python:3.12-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install minimal dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgtk-3-0 \
    libxss1 \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Create data directories
RUN mkdir -p /app/data/temp /app/data/servers /app/data/plugins

# Copy application code
COPY . .

# Create a non-root user for security
RUN groupadd -r spigot && useradd -r -g spigot -G audio,video spigot \
    && mkdir -p /home/spigot/Downloads \
    && chown -R spigot:spigot /app \
    && chown -R spigot:spigot /home/spigot

# Switch to non-root user
USER spigot

# Set Playwright to use installed browser
ENV PLAYWRIGHT_BROWSERS_PATH=/home/spigot/.cache/ms-playwright

# Start the application
CMD ["python", "-m", "src"]