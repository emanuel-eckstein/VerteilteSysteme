import time
import lgpio
import threading

# GPIO-Setup für den Raspberry Pi (GPIO2 ist Pin 27)
GPIO_PIN = 2  # Pin 2 für GPIO2
chip = None
timer = None
timer_lock = threading.Lock()

# Funktion zum Initialisieren des GPIO, wenn nicht schon geschehen
def init_gpio():
    global chip
    if chip is None:
        chip = lgpio.gpiochip_open(0)  # Öffne den ersten GPIO-Chip
        lgpio.gpio_claim_output(chip, GPIO_PIN)  # GPIO2 als Output deklarieren
        print("GPIO initialized.")

# Funktion zum Starten/Zurücksetzen des Timers
def reset_timer(duration):
    global timer

    # Initialisiere GPIO nur beim ersten Mal
    init_gpio()

    with timer_lock:
        if timer is not None:
            timer.cancel()  # Stoppe den alten Timer

        # Neuer Timer für die gegebene Dauer
        timer = threading.Timer(duration, turn_off_gpio)
        timer.start()

    # GPIO2 auf HIGH setzen (erneutes Setzen macht nichts, wenn schon HIGH)
    lgpio.gpio_write(chip, GPIO_PIN, 1)
    print(f"Pump is ON for {duration} seconds. Timer reset.")

# Funktion, die GPIO auf LOW setzt, wenn der Timer abläuft
def turn_off_gpio():
    if chip is not None:
        lgpio.gpio_write(chip, GPIO_PIN, 0)
        print("Pump is OFF. Timer finished.")

if __name__ == "__main__":
    duration = 10  # Die Dauer in Sekunden, wie lange die Pumpe eingeschaltet bleiben soll
    reset_timer(duration)
