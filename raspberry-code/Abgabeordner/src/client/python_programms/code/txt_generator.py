import random
import time
import os

# Pfade zu den Ordnern
signal_dir = '/home/admin/VS/signals'

# Speichern der letzten Prüfsummen für S1, S2 und S3
last_checksums = {
    "S1": None,
    "S2": None,
    "S3": None
}

# Variable zur Nummerierung der Dateien
file_counter = 0

# Schritt 1: Signal simulieren und als .txt Datei speichern
def simulate_signal_and_save():
    global file_counter
    
    # Zufallsentscheidung zwischen BF und BY
    suffix = random.choice(['BF', 'BY'])

    # Zufällige Zahl zwischen 1 und 3 für S_value
    s_value = random.randint(1, 3)
    s_key = f"S{s_value}"

    # Generiere die Zahl für 0000-1023 abhängig vom Suffix
    if suffix == 'BF':
        value_0000_1023 = random.randint(500, 1023)
        value_0000_1023_str = f"{value_0000_1023:04}"
    else:
        value_0000_1023 = random.randint(500, 1023)
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

    # Generiere einen durchnummerierten Präfix (000, 001, 002, ...)
    prefix = f"{file_counter:03}"
    file_counter += 1

    # Erstelle den Signalstring
    signal = f"{s_key}_{suffix}_{value_0000_1023_str}_{checksum}"

    # Erstelle den Dateinamen mit dem nummerierten Präfix
    signal_filename = f"{prefix}_{signal}.txt"
    signal_filepath = os.path.join(signal_dir, signal_filename)

    # Schreibe das Signal in die .txt Datei
    with open(signal_filepath, 'w') as f:
        f.write(signal)

    print(f"Signal gespeichert: {signal_filepath}")
    return signal_filepath

# Hauptschleife
def main():
    # Sicherstellen, dass das Verzeichnis existiert
    os.makedirs(signal_dir, exist_ok=True)

    while True:
        # Schritt 1: Signal generieren und speichern
        signal_filepath = simulate_signal_and_save()

        # 1 Sekunde warten, bevor ein neues Signal generiert wird
        time.sleep(1)

if __name__ == "__main__":
    main()
