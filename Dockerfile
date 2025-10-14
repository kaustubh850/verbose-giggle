FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip git build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Arduino CLI and AVR cores
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh && \
    arduino-cli core update-index && \
    arduino-cli core install arduino:avr

# Install Arduino libraries (continue even if some fail)
RUN arduino-cli lib install "Servo" || true \
 && arduino-cli lib install "Wire" || true \
 && arduino-cli lib install "EEPROM" || true \
 && arduino-cli lib install "LiquidCrystal" || true \
 && arduino-cli lib install "SoftwareSerial" || true \
 && arduino-cli lib install "SPI" || true \
 && arduino-cli lib install "Adafruit NeoPixel" || true \
 && arduino-cli lib install "Stepper" || true \
 && arduino-cli lib install "Adafruit GFX Library" || true \
 && arduino-cli lib install "Adafruit SSD1306" || true \
 && arduino-cli lib install "Adafruit SH1106" || true \
 && arduino-cli lib install "TouchScreen" || true \
 && arduino-cli lib install "TFT" || true \
 && arduino-cli lib install "TFT_eSPI" || true \
 && arduino-cli lib install "Adafruit ILI9341" || true \
 && arduino-cli lib install "Adafruit BusIO" || true \
 && arduino-cli lib install "Adafruit Sensor" || true \
 && arduino-cli lib install "Adafruit TCS34725" || true \
 && arduino-cli lib install "Adafruit Motor Shield" || true \
 && arduino-cli lib install "Adafruit PWM Servo Driver" || true \
 && arduino-cli lib install "Ultrasonic" || true \
 && arduino-cli lib install "DHT sensor library" || true \
 && arduino-cli lib install "Adafruit BNO055" || true \
 && arduino-cli lib install "Adafruit LSM9DS1" || true \
 && arduino-cli lib install "Adafruit INA219" || true


    
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
