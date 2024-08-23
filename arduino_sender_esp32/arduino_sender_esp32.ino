// Die Zeile mit der LoRa-Message muss entsprechend nach Sensornummer angepasst werden

// benötigte Bibliotheken
#include <SPI.h>
#include <LoRa.h>

// Analoger Pin A0 für den Sensor
int sensorPin = A0;  
// Analoger Pin A1 für die Batteriespannung
int voltagePin = A1;

// Digitaler PIN 5 für das Öffnen und Schließen des Ventils
int VENT = 5;               

// Definierter Grenzwert, unter dem eine Bewässerung gestartet werden soll
int threshold = 800;

// Definierte Sensornummer
String thisSensor = "S001";

void setup() {
  Serial.begin(9600);
  analogReadResolution(10); //setzt die Auflösung der anaolgen Input-Werte auf 0 bis 1023
  LoRa.setSpreadingFactor(7); // Werte von 7 bis 12 möglich
  LoRa.setSignalBandwidth(125E3); // Werte 125E3, 250E3 oder 500E3 möglich
  LoRa.setCodingRate4(8); // Werte von 5 (4/5) bis 8 (4/8) möglich

  digitalWrite(VENT, LOW);
  pinMode(VENT, OUTPUT);

  // Hiermit kann über den seriellen Monitor der Arduino IDE
  // ein Problem mit dem LoRa-Modul festgestellt werden
  Serial.println("LoRa Sender");
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
  }
}

void loop() {
  int potValue = analogRead(sensorPin); // Liest den Wert des Sensors
  int voltValue = analogRead(voltagePin); // Liest den Wert der Batteriespannung
  int finalValue = voltValue / 2; // Zeigt ungefähr die Akkuladung in % an, wird über 2 Widerstände per Spannungsteiler abgegriffen. Bei ca. 3,7V bei ist der Wert bei 100 (%), wenn der Akku geladen wird auch über ~140

  String Messergebnis = thisSensor + " " + String(potValue) + " Bodenfeuchtigkeit";
  String finalBatteryValue = String(finalValue) + "Batterieladung";

  // Jedes Messergebnis wird an das Pumpen-Kontrollzentrum gesendet und dort aufgezeichnet
  Serial.println(finalValue); 
  LoRa.beginPacket();
  LoRa.print(finalValue);
  LoRa.print("\n");
  LoRa.endPacket();
  delay(2000); // Verzögerung damit sich die Nachrichten nicht überlagern   
  Serial.println(Messergebnis); 
  LoRa.beginPacket();
  LoRa.print(Messergebnis);
  LoRa.print("\n");
  LoRa.endPacket();

  // Wenn der Wert unter dem Schwellenwert liegt
  if (potValue < threshold) {   
    //digitalWrite(VENT, HIGH); // öffnet das Ventil
    delay(5000); // 5 Sekunden Verzögerung, damit sich das Ventil vollständig öffnen kann

    // Sendet Signale an das Pumpen-Kontrollzentrum, um die Pumpe zu starten
    String ventOpen = thisSensor + "ON";
    Serial.println(ventOpen); 
    LoRa.beginPacket();
    LoRa.print(ventOpen);
    LoRa.print("\n");
    LoRa.endPacket();
    delay(6000UL); // Bewässerung für 10min, als unsigned long initiieren

    String ventClosed = thisSensor + "OFF";
    Serial.println(ventClosed);
    LoRa.beginPacket();
    LoRa.print(ventClosed);
    LoRa.print("\n");
    LoRa.endPacket();
    delay(5000); // 5 Sekunden Puffer damit es keinen Wasserschlag gibt
    //digitalWrite(VENT, LOW); // Ventil schließen
  }

  // Warte eine halbe Stunde bis zur nächsten Messung.
  delay(3000); 
}
