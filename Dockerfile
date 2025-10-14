FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y wget curl unzip git build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Arduino CLI and AVR cores
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh && \
    arduino-cli core update-index && \
    arduino-cli core install arduino:avr

RUN arduino-cli lib install "Servo"
RUN arduino-cli lib install "Wire"
RUN arduino-cli lib install "EEPROM"
RUN arduino-cli lib install "LiquidCrystal"
RUN arduino-cli lib install "SoftwareSerial"
RUN arduino-cli lib install "SPI"
RUN arduino-cli lib install "Adafruit NeoPixel"
RUN arduino-cli lib install "Stepper"
RUN arduino-cli lib install "Adafruit GFX Library"
RUN arduino-cli lib install "Adafruit SSD1306"
RUN arduino-cli lib install "Adafruit SH1106"
RUN arduino-cli lib install "TouchScreen"
RUN arduino-cli lib install "TFT"
RUN arduino-cli lib install "TFT_eSPI"
RUN arduino-cli lib install "Adafruit ILI9341"
RUN arduino-cli lib install "Adafruit BusIO"
RUN arduino-cli lib install "Adafruit Sensor"
RUN arduino-cli lib install "Adafruit TCS34725"
RUN arduino-cli lib install "Adafruit Motor Shield"
RUN arduino-cli lib install "Adafruit PWM Servo Driver"
RUN arduino-cli lib install "Ultrasonic"
RUN arduino-cli lib install "DHT sensor library"
RUN arduino-cli lib install "Adafruit BNO055"
RUN arduino-cli lib install "Adafruit LSM9DS1"
RUN arduino-cli lib install "Adafruit INA219"

    
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
