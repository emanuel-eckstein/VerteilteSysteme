import os
import json
import re
import time
from shutil import move
from transitions import Machine

# Pfade zu den Ordnern
signal_dir = '/home/admin/VS/signals'
processed_dir = '/home/admin/VS/processed'  # Verarbeitete Dateien werden hierhin verschoben
json_dir = '/home/admin/VS/json_files'

# Sicherstellen, dass die Verzeichnisse existieren
os.makedirs(signal_dir, exist_ok=True)
os.makedirs(json_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

class SignalStateMachine(object):
    states = ['start', 'S1', 'S2', 'S3', 'checksum_error', 'syntax_semantic_error', 
              'water_error', 'battery_error', 'convert_txt_to_json', 'end']

    def __init__(self):
        self.last_values = {
            "S1_BF": None,
            "S2_BF": None,
            "S3_BF": None
        }
        self.machine = Machine(model=self, states=SignalStateMachine.states, initial='start')

        # Define transitions
        self.machine.add_transition(trigger='new_file', source='start', dest='S1', conditions=['is_S1_file'])
        self.machine.add_transition(trigger='new_file', source='start', dest='S2', conditions=['is_S2_file'])
        self.machine.add_transition(trigger='new_file', source='start', dest='S3', conditions=['is_S3_file'])

        # Handle checksum errors
        self.machine.add_transition(trigger='checksum_error', source='*', dest='checksum_error', after='handle_checksum_error')

        # Handle syntax/semantic errors
        self.machine.add_transition(trigger='syntax_semantic_error', source='*', dest='syntax_semantic_error', after='handle_syntax_error')

        # Handle water-related errors (sensor-wide comparison)
        self.machine.add_transition(trigger='water_error', source='*', dest='water_error', after='handle_water_error')

        # Handle battery-related errors
        self.machine.add_transition(trigger='battery_error', source='S1', dest='battery_error', after='handle_battery_error')

        # Convert txt to json
        self.machine.add_transition(trigger='convert_to_json', source='*', dest='convert_txt_to_json', after='convert_txt_to_json_file')
        self.machine.add_transition(trigger='complete_conversion', source='convert_txt_to_json', dest='end')

        # Reset the machine back to start state after processing each file
        self.machine.add_transition(trigger='reset', source='*', dest='start')

    # Conditions to detect S1, S2, and S3 files
    def is_S1_file(self, filename):
        return '_S1_' in filename

    def is_S2_file(self, filename):
        return '_S2_' in filename

    def is_S3_file(self, filename):
        return '_S3_' in filename

    # Check for checksum errors
    def check_checksum(self, filename):
        match = re.search(r'_(\d{2})\.txt$', filename)
        if match:
            checksum = match.group(1)
            s_value = filename.split('_')[1]
            last_checksum = self.last_values.get(s_value)
            if last_checksum and last_checksum[-1] != checksum[0]:
                return False
            self.last_values[s_value] = checksum
        return True

    def check_water_error(self, filename):
        # Example: XXX_S1_BF_0336_88.txt, Check for sensor-wide BF values
        match = re.search(r'_(S[1-3])_BF_(\d{4})_', filename)
        if match:
            sensor = match.group(1) + "_BF"  # z.B. S1_BF
            value = int(match.group(2))
            print(f"Detected {sensor} with value: {value}")  # Debug

            last_value = self.last_values.get(sensor)
            if last_value is not None and last_value < 500 and value < last_value:
                print(f"Water error: {sensor} value {value} is lower than previous {last_value}")
                return True

            # Aktualisiere den letzten Wert für den Sensor
            self.last_values[sensor] = value
        return False

    def check_battery_error(self, filename):
        # Example: XXX_S1_BY_0941_28.txt, check if value < 500
        match = re.search(r'_BY_(\d{4})_', filename)
        if match:
            value = int(match.group(1))
            print(f"Battery value detected: {value}")  # Debug
            return value < 500
        return False

    # Log and output error messages
    def handle_checksum_error(self):
        print("Checksum error: g10 y1010")
        self.save_error_json("PS")
        # Nach Fehlerbehandlung Datei in JSON umwandeln
        self.convert_to_json(self.current_file)
        self.complete_conversion(self.current_file)

    def handle_syntax_error(self):
        print("Syntax/Semantic error: g10 y0 r 0")
        self.save_error_json("SS")
        # Bei SS-Fehler keine JSON-Konvertierung

    def handle_water_error(self):
        print("Water error: g0 y1010 r[10*(X][von SX])")
        self.save_error_json("BS")
        # Nach Fehlerbehandlung Datei in JSON umwandeln
        self.convert_to_json(self.current_file)
        self.complete_conversion(self.current_file)

    def handle_battery_error(self):
        print("Battery error: g0 y10 r[10*(X][von SX])")
        self.save_error_json("BN")
        # Nach Fehlerbehandlung Datei in JSON umwandeln
        self.convert_to_json(self.current_file)
        self.complete_conversion(self.current_file)

    def save_error_json(self, error_type):
        error_data = {"error": error_type}
        error_filename = f"error_{error_type}_{self.current_file.replace('.txt', '.json')}"
        error_filepath = os.path.join(json_dir, error_filename)
        try:
            with open(error_filepath, 'w') as f:
                json.dump(error_data, f, indent=4)
            print(f"Error saved in JSON file: {error_filepath}")
        except Exception as e:
            print(f"Fehler beim Speichern der Fehler-JSON-Datei: {e}")

    # Convert .txt to .json file
    def convert_txt_to_json_file(self, filename):
        parts = filename.split('_')
        s_value = parts[1][1]  # 'S' gefolgt von der Zahl
        suffix = parts[2]
        value = parts[3]

        json_data = {
            "suffix": suffix,
            "S_value": s_value,
            "value": value
        }
        json_filename = f"{filename.replace('.txt', '.json')}"
        json_filepath = os.path.join(json_dir, json_filename)

        try:
            with open(json_filepath, 'w') as f:
                json.dump(json_data, f, indent=4)
            print(f"Converted .txt to .json and saved at: {json_filepath}")
        except Exception as e:
            print(f"Fehler beim Speichern der JSON-Datei: {e}")

    def move_processed_file(self, filepath):
        filename = os.path.basename(filepath)
        try:
            move(filepath, os.path.join(processed_dir, filename))
            print(f"Datei nach Verarbeitung verschoben: {filepath} -> {processed_dir}")
        except Exception as e:
            print(f"Fehler beim Verschieben der Datei: {e}")

    def process_file(self, filepath):
        filename = os.path.basename(filepath)
        self.current_file = filename  # Für Fehlerberichte
        # Trigger the new_file event with the filename
        self.new_file(filename)

        # Check for checksum error
        if not self.check_checksum(filename):
            self.checksum_error()
        # Check for syntax/semantic error (hier angenommen, falls Dateiname nicht dem erwarteten Muster entspricht)
        elif not re.match(r'^\d{3}_S[1-3]_(BF|BY)_\d{4}_\d{2}\.txt$', filename):
            self.syntax_semantic_error()
        else:
            error_occurred = False
            # Check for water error (sensor-wide BF values)
            if 'BF' in filename and self.check_water_error(filename):
                self.water_error()
                error_occurred = True

            # Check for battery error in BY files
            if 'BY' in filename and self.check_battery_error(filename):
                self.battery_error()
                error_occurred = True

            # Wenn kein Syntax/Semantikfehler auftritt, erstelle die reguläre JSON-Datei
            if self.state != 'syntax_semantic_error':
                self.convert_to_json(filename)
                self.complete_conversion(filename)

        # Datei nach Verarbeitung verschieben
        self.move_processed_file(filepath)
        # State Machine zurücksetzen
        self.reset()

# Hauptschleife, um Dateien zu verarbeiten
def main():
    machine = SignalStateMachine()

    while True:
        files = sorted([os.path.join(signal_dir, f) for f in os.listdir(signal_dir) if f.endswith('.txt')])
        for file in files:
            print(f"Processing file: {file}")  # Debug: Anzeigen der zu verarbeitenden Datei
            machine.process_file(file)
        time.sleep(1)

if __name__ == "__main__":
    main()


!!!
TESTDATEI
!!!
000_S1_BY_0194_97.json  003_S2_BF_0671_84.json  006_S1_BY_0714_95.json  009_S3_BF_0290_24.json           error_BS_005_S2_BF_0199_19.json
001_S1_BY_0693_71.json  004_S2_BF_0211_41.json  007_S1_BY_1000_22.json  010_S3_BF_0395_91.json           error_PS_006_S1_BY_0714_95.json
002_S1_BF_0673_12.json  005_S2_BF_0199_19.json  008_S3_BF_0215_32.json  error_BN_000_S1_BY_0194_97.json  error_PS_010_S3_BF_0395_91.json
