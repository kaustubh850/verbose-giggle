FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip git build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Arduino CLI and AVR cores
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh && \
    arduino-cli core update-index && \
    arduino-cli core install arduino:avr

    
# Set working directory
WORKDIR /workspace

# Install Python deps for API
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy app
COPY app /app
WORKDIR /app
# Expose FastAPI port
EXPOSE 5000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]
