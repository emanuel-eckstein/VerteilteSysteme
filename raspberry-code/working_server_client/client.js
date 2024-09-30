const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

// WebSocket-Verbindung zum Server
const ws = new WebSocket('ws://192.168.0.88:8080');

// Pfad zum Ordner, der die JSON-Dateien enthält
const directoryPath = '/home/admin/VS/json_files';

// Funktion zum Senden der Nachrichten mit 10 Sekunden Pause
function sendData(file) {
  const filePath = path.join(directoryPath, file);

  // Lese die JSON-Datei und sende sie an den Server
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Fehler beim Lesen der Datei:', err);
      return;
    }

    // Nachricht im JSON-Format an den Server senden
    try {
      const message = JSON.parse(data);
      message.timestamp = new Date().toISOString().split('.')[0];  // Füge die aktuelle Zeit zur Nachricht hinzu
      ws.send(JSON.stringify(message));
      console.log(`Sent: ${JSON.stringify(message)}`);
    } catch (e) {
      console.error('Fehler beim Verarbeiten der JSON-Datei:', e);
    }
  });
}

// WebSocket-Verbindung herstellen und Nachrichten senden, sobald die Verbindung geöffnet ist
ws.on('open', function open() {
  console.log('Verbindung zum Server hergestellt');

  // Lese alle vorhandenen Dateien im Verzeichnis und sende sie nacheinander
  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      console.error('Fehler beim Lesen des Verzeichnisses:', err);
      return;
    }

    // Sende die vorhandenen Dateien
    files.forEach((file, index) => {
      setTimeout(() => sendData(file), index * 10000);  // 10 Sekunden Pause zwischen den Dateien
    });
  });

  // Überwache den Ordner auf neue Dateien
  fs.watch(directoryPath, (eventType, filename) => {
    if (eventType === 'rename' && filename) {
      console.log(`Neue Datei erkannt: ${filename}`);
      setTimeout(() => sendData(filename), 1000);  // 1 Sekunde Pause vor dem Senden
    }
  });
});
