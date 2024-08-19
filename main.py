import asyncio
from bleak import BleakClient
import time
import pyvisa

# Define the UUIDs of the BLE service and characteristic
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

class PIcontroller:
    def __init__(self):
        self.errors = []
        print("init!")
    def PI(self,SP,PV):
        ###error + proportion###
        et = SP - PV
        self.errors.append(et)
        ###integral###
        i = sum(self.errors)
        d = 0
        if len(self.errors) > 1:
            x = list(range(len(self.errors)))
            fd = [(self.errors[i + 1] - self.errors[i]) / (x[i + 1] - x[i]) for i in range(len(self.errors) - 1)]
            d = sum(fd)/len(fd)
            print(d)

        ut = pgain*et + igain*i + dgain*d
        npv = PV + ut

        return(npv)



async def run(address):
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")

        # Read the value of the characteristic
        data = await client.read_gatt_char(CHARACTERISTIC_UUID)
        print("Received data:", data.decode('utf-8'))

        # Optional: Continuously read data if needed
        while True:
            try:
                data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                print("Received data:", data.decode('utf-8'))
                await asyncio.sleep(.2)  # Read every 2 seconds

            except Exception as e:
                print(f"Error: {e}")
                break

def main(address):
    xcon = PIcontroller()
    ycon = PIcontroller()
    zcon = PIcontroller()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))

if __name__ == "__main__":
    device_address = 'b9:e9:78:3f:10:da'
    main(device_address)

