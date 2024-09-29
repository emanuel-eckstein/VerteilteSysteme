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

// WebSocket-Server: Verarbeite eingehende Nachrichten
wss.on('connection', ws => {
  // Sende die gespeicherten Graph-Daten und Zeitstempel an den neuen Client, wenn er sich verbindet
  ws.send(JSON.stringify({ graphs, timeStamps }));

  ws.on('message', message => {
    const parsedMessage = JSON.parse(message);

    // Extrahiere Sensor, Suffix, Wert und Zeitstempel
    const { sensor, suffix, value, timestamp } = parsedMessage;
    const graphKey = `${sensor}_B${suffix}`;

    // Wert und Zeitstempel in den entsprechenden Graph einfügen, wenn der Graph existiert
    if (graphs[graphKey]) {
      graphs[graphKey].push(parseInt(value, 10));
      timeStamps[graphKey].push(timestamp);  // Füge den Zeitstempel hinzu
      console.log(`Updated graph ${graphKey} with value ${value} at ${timestamp}`);
    }

    // Sende die aktualisierten Graph-Daten und Zeitstempel an alle verbundenen Clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({ graphs, timeStamps }));
      }
    });
  });
});

// Statische Dateien aus dem Ordner "public" bereitstellen
app.use(express.static(path.join(__dirname, 'public')));

// Server auf Port 8080 starten
server.listen(8080, () => {
  console.log('Server läuft auf http://<Raspberry-Pi-IP>:8080');
});
