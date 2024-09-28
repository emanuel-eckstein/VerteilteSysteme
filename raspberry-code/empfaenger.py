import sys
from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD

# Set up the board
BOARD.setup()

class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

        # Set the frequency to 433 MHz and enable CRC
        self.set_freq(433.0)
        self.set_pa_config(pa_select=1)  # Power amplifier settings
        self.set_rx_crc(True)  # Enable CRC to ensure message integrity

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

        while True:
            sleep(1)  # Increase delay between packet reads
            sys.stdout.flush()

    def on_rx_done(self):
        print("\nReceived: ")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        message = bytes(payload).decode("utf-8", 'ignore').strip()

        # Print message only if it's complete and valid
        if len(message) > 0:
            print(message)

        # Reset the mode to continue receiving
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

# Create an instance of the LoRa receiver
lora = LoRaRcvCont(verbose=False)

# Set mode to standby before starting
lora.set_mode(MODE.STDBY)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
