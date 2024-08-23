from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import sys

BOARD.setup()

class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.buffer = ""  # Buffer to store incomplete messages

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            # Wait for interrupt on RX_DONE to process message
            sys.stdout.flush()

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        message = bytes(payload).decode("utf-8", 'ignore')

        # Check the message length
        if len(message) > 0:
            self.buffer += message  # Append received message to the buffer

            # Process complete messages immediately
            if '\n' in self.buffer:
                messages = self.buffer.split('\n')
                for msg in messages[:-1]:
                    print(msg.strip())  # Print each complete message
                self.buffer = messages[-1]  # Keep the last incomplete message in the buffer

        # Return to receiving mode quickly
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)

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