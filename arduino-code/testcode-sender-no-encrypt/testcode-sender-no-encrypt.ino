#include <SPI.h>
#include <LoRa.h>

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  // Begin LoRa at 433 MHz
  if (!LoRa.begin(433E6)) {
    while (1) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(200);
      digitalWrite(LED_BUILTIN, LOW);
      delay(200);
    }
  }

  // Enable CRC to ensure message integrity
  LoRa.enableCrc();
}

void loop() {
  // Start sending a packet
  LoRa.beginPacket();
  
  // Cast the message to const uint8_t* to match the write method's expected type
  LoRa.write((const uint8_t*)"Hello World", 11);  // Send exactly 11 bytes
  
  // End the packet
  LoRa.endPacket();

  // Flash the built-in LED to indicate message sent
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(2000);  // Increase the delay between transmissions
}
