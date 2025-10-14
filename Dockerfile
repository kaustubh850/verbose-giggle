FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip git build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Arduino CLI and AVR cores
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh && \
    arduino-cli core update-index && \
    arduino-cli core install arduino:avr

# Install a big set of common Arduino libraries
RUN arduino-cli lib install "Servo" \
    && arduino-cli lib install "Wire" \
    && arduino-cli lib install "EEPROM" \
    && arduino-cli lib install "LiquidCrystal" \
    && arduino-cli lib install "SoftwareSerial" \
    && arduino-cli lib install "SPI" \
    && arduino-cli lib install "Adafruit NeoPixel" \
    && arduino-cli lib install "Stepper" \
    && arduino-cli lib install "Adafruit GFX Library" \
    && arduino-cli lib install "Adafruit SSD1306" \
    && arduino-cli lib install "Adafruit SH1106" \
    && arduino-cli lib install "TouchScreen" \
    && arduino-cli lib install "TFT" \
    && arduino-cli lib install "TFT_eSPI" \
    && arduino-cli lib install "Adafruit ILI9341" \
    && arduino-cli lib install "Adafruit BusIO" \
    && arduino-cli lib install "Adafruit Sensor" \
    && arduino-cli lib install "Adafruit TCS34725" \
    && arduino-cli lib install "Adafruit Motor Shield" \
    && arduino-cli lib install "Adafruit PWM Servo Driver" \
    && arduino-cli lib install "Ultrasonic" \
    && arduino-cli lib install "DHT sensor library" \
    && arduino-cli lib install "Adafruit BNO055" \
    && arduino-cli lib install "Adafruit LSM9DS1" \
    && arduino-cli lib install "Adafruit INA219"
    
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

CMD ["python3", "server.py"]
