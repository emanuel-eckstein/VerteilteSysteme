#kritischer Bereich 190-199, BF steigt danach nicht auf
#kritischer Bereich 490-499, BY zu gering

import random
import time

def generate_message(previous_bf=None, previous_by=None, previous_bf_value=None):
    # Zufällige Zahl zwischen 1 und 3 für S
    s_value = random.randint(1, 3)

    # Zufallsentscheidung zwischen BF und BY
    suffix = random.choice(['BF', 'BY'])

    # Generiere die Zahl für 0000-1023 abhängig vom Suffix
    if suffix == 'BF':
        if previous_bf_value is not None and previous_bf_value < 190:
            # Setze die Zahl auf exakt 500, wenn vorheriger Wert unter 190 war
            value_0000_1023 = 500
        else:
            # Zufällige Zahl zwischen 0 und 1023 für BF
            value_0000_1023 = random.randint(0, 1023)

        value_0000_1023_str = f"{value_0000_1023:04}"

        if previous_bf:
            # Verwende die letzte Ziffer der vorherigen BF-Prüfsumme als erste Ziffer
            first_checksum_digit = previous_bf[-1]
        else:
            # Falls keine vorherige BF-Prüfsumme, zufällig eine Zahl zwischen 1 und 9 generieren
            first_checksum_digit = str(random.randint(1, 9))

        second_checksum_digit = str(random.randint(1, 9))
        checksum = f"{first_checksum_digit}{second_checksum_digit}"
    else:
        # Zufällige Zahl zwischen 490 und 1023 für BY
        value_0000_1023 = random.randint(490, 1023)
        value_0000_1023_str = f"{value_0000_1023:04}"

        if previous_by:
            # Verwende die letzte Ziffer der vorherigen BY-Prüfsumme als erste Ziffer
            first_checksum_digit = previous_by[-1]
        else:
            # Falls keine vorherige BY-Prüfsumme, zufällig eine Zahl zwischen 1 und 9 generieren
            first_checksum_digit = str(random.randint(1, 9))

        second_checksum_digit = str(random.randint(1, 9))
        checksum = f"{first_checksum_digit}{second_checksum_digit}"

    # Zusammensetzen der Nachricht
    message = f"S{s_value}_{suffix}_{value_0000_1023_str}_{checksum}"

    return message, suffix, checksum, value_0000_1023

def main():
    previous_bf = None  # Um die letzte Prüfsumme für BF zu speichern
    previous_by = None  # Um die letzte Prüfsumme für BY zu speichern
    previous_bf_value = None  # Um den vorherigen Wert für BF zu speichern

    while True:
        # Neue Nachricht generieren
        message, suffix, checksum, value_0000_1023 = generate_message(previous_bf, previous_by, previous_bf_value)

        # Ausgabe auf der Konsole
        print(message)

        # Prüfsumme und Wert für die nächste Nachricht speichern, je nach Suffix
        if suffix == 'BF':
            previous_bf = checksum
            previous_bf_value = value_0000_1023
        else:
            previous_by = checksum

        # 1 Sekunde warten
        time.sleep(1)

if __name__ == "__main__":
    main()
