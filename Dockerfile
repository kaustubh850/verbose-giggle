FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip git build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Arduino CLI
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh

# Set working directory
WORKDIR /workspace

# Install Python deps for API
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy app
COPY app /app
WORKDIR /app

CMD ["python3", "server.py"]
