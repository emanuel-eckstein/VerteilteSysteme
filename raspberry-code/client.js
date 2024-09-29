const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

// WebSocket-Verbindung zum Server
const ws = new WebSocket('ws://192.168.0.88:8080');

// Pfad zum Ordner, der die JSON-Dateien enthält
const directoryPath = '/home/admin/VS/json_files';

// Funktion zum Senden der Daten mit 10 Sekunden Pause
function sendData(files) {
  let index = 0;

  function sendNextFile() {
    if (index < files.length) {
      const file = files[index];
      // Regex angepasst, um die ersten drei zufälligen Ziffern zu ignorieren
      const match = file.match(/\d{3}_(S[1-3])_B(F|Y)_(\d{4})_(\d{2})/);
      if (match) {
        const [_, sensor, suffix, value] = match;

        // Aktuelle Uhrzeit hinzufügen
        const timestamp = new Date().toISOString().split('.')[0];
        const message = {
          sensor,
          suffix,
          value,
          timestamp // Füge die aktuelle Zeit zur Nachricht hinzu
        };

        // Nachricht im JSON-Format an den Server senden
        ws.send(JSON.stringify(message));
        console.log(`Sent: ${JSON.stringify(message)}`);

        // Nach dem Senden 10 Sekunden warten, bevor die nächste Datei gesendet wird
        index++;
        setTimeout(sendNextFile, 1000);  // 10 Sekunden Pause
      } else {
        // Wenn der Dateiname nicht passt, direkt zur nächsten Datei
        index++;
        sendNextFile();
      }
    }
  }

  // Starte den Versand der ersten Datei
  sendNextFile();
}

ws.on('open', function open() {
  console.log('Verbindung zum Server hergestellt');

  // Lese alle Dateien im Verzeichnis und sende sie nacheinander
  fs.readdir(directoryPath, (err, files) => {
    if (err) {
      console.error('Fehler beim Lesen des Verzeichnisses:', err);
      return;
    }

    // Starte den Versand der Daten mit einer Pause von 10 Sekunden
    sendData(files);
  });
});
