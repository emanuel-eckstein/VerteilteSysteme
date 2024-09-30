const WebSocket = require('ws');
const express = require('express');
const http = require('http');
const path = require('path');

// Express-App und HTTP-Server erstellen
const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Graph-Datenstrukturen für die sechs Graphen
let graphs = {
  S1_BF: [],
  S1_BY: [],
  S2_BF: [],
  S2_BY: [],
  S3_BF: [],
  S3_BY: []
};

let timeStamps = {
  S1_BF: [],
  S1_BY: [],
  S2_BF: [],
  S2_BY: [],
  S3_BF: [],
  S3_BY: []
};

// Array für die letzten 5 Warnungen
let warningMessages = [];

// WebSocket-Server: Verarbeite eingehende Nachrichten
wss.on('connection', ws => {
  // Sende die gespeicherten Graph-Daten, Zeitstempel und Warnungen an den neuen Client, wenn er sich verbindet
  ws.send(JSON.stringify({ graphs, timeStamps, warnings: warningMessages }));

  ws.on('message', message => {
    const parsedMessage = JSON.parse(message);

    // Prüfe, ob es sich um eine Warnung oder ein Datenpunkt-Update handelt
    if (parsedMessage.error) {
      // Verarbeite Warnungen
      const warning = {
        error: parsedMessage.error,
        timestamp: parsedMessage.timestamp
      };

      // Füge die neue Warnung zum Array hinzu und halte nur die letzten 5 Warnungen
      warningMessages.push(warning);
      if (warningMessages.length > 9) {
        warningMessages.shift();  // Entfernt die älteste Warnung
      }

      console.log(`Received warning: ${parsedMessage.error} at ${parsedMessage.timestamp}`);

      // Sende die aktualisierten Warnungen an alle verbundenen Clients
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({ warnings: warningMessages }));
        }
      });

    } else if (parsedMessage.S_value && parsedMessage.suffix && parsedMessage.value && parsedMessage.timestamp) {
      // Verarbeite Datenpunkt-Updates
      const sensor = `S${parsedMessage.S_value}`;  // Erstelle den Sensornamen (z.B. S1, S2, S3)
      const { suffix, value, timestamp } = parsedMessage;

      // Überprüfe, ob der Suffix korrekt ist (sollte nur 'BF' oder 'BY' sein)
      const validSuffix = (suffix === 'BF' || suffix === 'BY') ? suffix : null;

      if (validSuffix) {
        const graphKey = `${sensor}_${validSuffix}`;  // Erstelle den graphKey, z.B. S1_BF oder S2_BY

        // Wert und Zeitstempel in den entsprechenden Graph einfügen, wenn der Graph existiert
        if (graphs[graphKey]) {
          graphs[graphKey].push(parseInt(value, 10));
          timeStamps[graphKey].push(timestamp);  // Füge den Zeitstempel hinzu
          console.log(`Updated graph ${graphKey} with value ${value} at ${timestamp}`);
        } else {
          console.log(`Graph ${graphKey} existiert nicht.`);
        }

        // Sende die aktualisierten Graph-Daten und Zeitstempel an alle verbundenen Clients
        wss.clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ graphs, timeStamps }));
          }
        });
      } else {
        console.error(`Ungültiger Suffix erhalten: ${suffix}`);
      }

    } else {
      console.error('Unbekannte Nachricht erhalten:', parsedMessage);
    }
  });
});

// Statische Dateien aus dem Ordner "public" bereitstellen
app.use(express.static(path.join(__dirname, 'public')));

// Server auf Port 8080 starten
server.listen(8080, () => {
  console.log('Server läuft auf http://<Raspberry-Pi-IP>:8080');
});
