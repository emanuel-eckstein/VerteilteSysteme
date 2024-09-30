import random
import time
import os
import json

# Pfade zu den Ordnern
signal_dir = '/home/admin/VS/signals'
json_dir = '/home/admin/VS/json_files'

# Speichern der letzten Prüfsummen für S1, S2 und S3
last_checksums = {
    "S1": None,
    "S2": None,
    "S3": None
}

# Schritt 1: Signal simulieren und als .txt Datei speichern
def simulate_signal_and_save():
    # Zufallsentscheidung zwischen BF und BY
    suffix = random.choice(['BF', 'BY'])
    
    # Zufällige Zahl zwischen 1 und 3 für S_value
    s_value = random.randint(1, 3)
    s_key = f"S{s_value}"
    
    # Generiere die Zahl für 0000-1023 abhängig vom Suffix
    if suffix == 'BF':
        value_0000_1023 = random.randint(0, 1023)
        value_0000_1023_str = f"{value_0000_1023:04}"
    else:
        value_0000_1023 = random.randint(490, 1023)
        value_0000_1023_str = f"{value_0000_1023:04}"
    
    # Prüfsumme generieren
    if last_checksums[s_key] is None:
        # Falls es noch keine vorherige Prüfsumme gibt, wähle eine zufällige Zahl als Startwert
        first_checksum_digit = str(random.randint(1, 9))
    else:
        # Verwende die letzte Ziffer der vorherigen Prüfsumme als erste Ziffer
        first_checksum_digit = last_checksums[s_key][-1]
    
    second_checksum_digit = str(random.randint(1, 9))
    checksum = f"{first_checksum_digit}{second_checksum_digit}"
    
    # Speichern der aktuellen Prüfsumme für das nächste Mal
    last_checksums[s_key] = checksum
    
    # Generiere 3 zufällige Ziffern für den Dateinamen
    random_prefix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    
    # Erstelle den Signalstring
    signal = f"{s_key}_{suffix}_{value_0000_1023_str}_{checksum}"
    
    # Erstelle den Dateinamen mit dem zufälligen Präfix
    signal_filename = f"{random_prefix}_{signal}.txt"
    signal_filepath = os.path.join(signal_dir, signal_filename)
    
    with open(signal_filepath, 'w') as f:
        f.write(signal)
    
    print(f"Signal gespeichert: {signal_filepath}")
    return signal, signal_filepath, random_prefix

# Schritt 2: TXT-Datei in JSON umwandeln und als .json Datei speichern
def convert_txt_to_json(txt_filepath, signal, random_prefix):
    # Zerlege das Signal in seine Teile
    parts = signal.split('_')
    s_value = parts[0][1]  # 'S' gefolgt von der Zahl
    suffix = parts[1]
    value = parts[2]
    checksum = parts[3]
    
    # Erstelle die JSON-Datenstruktur
    message_data = {
        "suffix": suffix,
        "S_value": s_value,
        "value": value,
        "checksum": checksum
    }
    
    # Erstelle den Namen für die .json Datei (mit zufälligem Präfix)
    json_filename = f"{random_prefix}_{signal}.json"
    json_filepath = os.path.join(json_dir, json_filename)
    
    # Speichere die JSON-Daten als .json Datei
    with open(json_filepath, 'w') as f:
        json.dump(message_data, f, indent=4)
    
    print(f"JSON Datei gespeichert: {json_filepath}")
    
    return json_filepath

# Schritt 3: Lösche die .txt Datei
def delete_txt_file(txt_filepath):
    if os.path.exists(txt_filepath):
        os.remove(txt_filepath)
        print(f"TXT Datei gelöscht: {txt_filepath}")

# Hauptschleife
def main():
    # Sicherstellen, dass die Verzeichnisse existieren
    os.makedirs(signal_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)

    while True:
        # Schritt 1: Signal generieren und speichern
        signal, txt_filepath, random_prefix = simulate_signal_and_save()

        # Überprüfen, ob eine .txt Datei existiert
        if os.path.exists(txt_filepath):
            # Schritt 2: TXT in JSON umwandeln und speichern
            json_filepath = convert_txt_to_json(txt_filepath, signal, random_prefix)
            
            # Schritt 3: Lösche die .txt Datei
            delete_txt_file(txt_filepath)
        
        # 1 Sekunde warten, bevor ein neues Signal generiert wird
        time.sleep(1)

if __name__ == "__main__":
    main()
