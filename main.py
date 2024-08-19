import asyncio
from bleak import BleakClient

# Define the UUIDs of the BLE service and characteristic
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

class PIcontroller:
    def __init__(self):
        self.errors = []
        print("init!")

    def PI(self, SP, PV):
        # Compute control output
        et = SP - PV
        self.errors.append(et)
        i = sum(self.errors)
        d = 0
        if len(self.errors) > 1:
            x = list(range(len(self.errors)))
            fd = [(self.errors[i + 1] - self.errors[i]) / (x[i + 1] - x[i]) for i in range(len(self.errors) - 1)]
            d = sum(fd) / len(fd)
            print(d)

        ut = pgain * et + igain * i + dgain * d
        npv = PV + ut

        return npv

async def run(addresses):
    clients = [BleakClient(address) for address in addresses]

    try:
        # Connect to all devices
        await asyncio.gather(*[client.connect() for client in clients])
        print(f"Connected to devices: {[client.address for client in clients]}")

        # Function to read data from a single client
        async def read_data(client):
            try:
                while True:
                    data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    print(f"Received data from {client.address}: {data.decode('utf-8')}")
                    await asyncio.sleep(2)  # Read every 2 seconds
            except Exception as e:
                print(f"Error with {client.address}: {e}")

        # Start reading data from each BLE device
        await asyncio.gather(*[read_data(client) for client in clients])

    except Exception as e:
        print(f"Failed to connect or read data: {e}")

    finally:
        # Disconnect from all devices
        await asyncio.gather(*[client.disconnect() for client in clients])
        print("Disconnected from all devices")

def main():
    addresses = ['b9:e9:78:3f:10:da','9e:9d:53:fa:dc:16']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(addresses))

if __name__ == "__main__":
    main()

