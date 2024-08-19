####                                                        ####
#### UNFINISHED :: DO NOT RUN WITH > 3 SUPPLIES (or at all) ####
####        COMPLETELY UNTESTED POWERSUPPLY FUNCTIONS       ####


#### TODO [highest to lowest priority] ####

#### 1. SET UP WIRING
#### 2. FIX VECTOR ADJUST TO USE TRIG (DO THE MATH RIGHT!)
#### 3. FIX POWER SUPPLY ORDERING
#### 4. WAY TO ADJUST VALUES 
#### 5. CHANGE PID WEIGHTS 
#### 6. SENSOR RANGE RESTRAINTS


import time
import pyvisa
import asyncio
from bleak import BleakClient
from numpy import matmul
ax = 0.0
ay = 0.0
az = 0.0
# Define the UUIDs of the BLE service and characteristic
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"
sensor1 = [0.0,0.0,0.0]
sensor2 = [0.0,0.0,0.0]



def consolebrick(): # just for formatting #
    print('\n')
    a = '#'
    for i in range(5):
        print(a*30)
    print('\n')


#####POWER CONTROL#####
def VectorWrite(i,j,k,sec): #floats < 1, only
    vector = [i,j,k]

    if sec:
        start = 3
    else: 
        start = 0 
    count = 0
    while count < 3:
        powersup(20,vector[count],devices[count+start])
        count+= 1
            #high v limit just incase, tune if it doesn't work. I can't do that without the supplies

def powersup(voltage, currentlim, device):
    raw = ('*RST#'
    ':SOUR:FUNC VOLT#'
    f':SOUR:VOLT {voltage}#'
    f':SOUR:VOLT:ILIM {currentlim}#'
    f':TRIG:LOAD "SimpleLoop", 1, 1#' ## prob dont need this. will test
    ':OUTP ON#'
    ':INIT#'
    '*WAI#'
    #':OUTP OFF'
    ).format(voltage=voltage, currentlim=currentlim, time=time)
#   print(raw)
    instructions = raw.split('#') # '#'s only serve as seperators
#    print(instructions)
    for i in instructions: # instructions string can be sent all at once with different formatting,
        device.write(i)    # this method helped with debugging/learning the commands. change if you
                           # deem it fit.
#####POWER CONTROL#####


#####CONTROL LOOP#####
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
#####CONTROL LOOP#####


#########################
##### MAIN FUNCTION #####
async def run(addresses):
    clients = [BleakClient(address) for address in addresses]

    try:
        # Connect to all devices
        await asyncio.gather(*[client.connect() for client in clients])
        print(f"Connected to devices: {[client.address for client in clients]}")

        # Function to read data from a single client
        async def read_data(client):
            try:


                ##### MAIN LOOP #####
                while True:
                    data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    print(f"Received data from {client.address}: {data.decode('utf-8')}")
                    data_str = data.decode('utf-8')
                    data_list = data_str.split(',')
                    n = 0 
                    while n < len(data_list):
                        if n > 0:
                            data_list[n] = float(data_list[n])
                        else:
                            data_list[n] = int(data_list[n]) # to use inbuilt index, i dont want to work with addr
                        n += 1
                    if data_list[0] == 1:
                        sensor1 = data_list
                    else:
                        sensor2 = data_list

                    adjustx = xcon.PI(sensor1[0],sensor2[0])
                    adjusty = ycon.PI(sensor1[0],sensor2[0])
                    adjustz = zcon.PI(sensor1[0],sensor2[0])

                    ### degree values vs 0 -> 1.0 for powersupplies. divide by 360 goes from degree to current
                    ### maybe. Irl probably not how it works. Fiddle with the values/device order.
                    ### Above is the biggest thing to work on. If im out of it (consequences of all nighter),
                    ### please look into this.

                    ### ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

                    ### https://stackoverflow.com/questions/14607640/rotating-a-vector-in-3d-space
                    ### what I have may look vaguely right for the purposes of a crappy demo, but
                    ### we oughta set up proper rotation matrices

                    vec_update = []
                    for i in [adjustx, adjusty, adjustz]:
                        vec_update.append(i/360)

                    ax += vec_update[0]
                    ay += vec_update[1]
                    az += vec_update[2]

                    VectorWrite(ax,ay,az,True) ### write updated values to second set of powersupplies
                    
                    ### vec_update will be added to list of currents abd ->SHOULD<- directly respond.
                    ### in my dreams ...
                    await asyncio.sleep(.2)  # Read every .2 seconds
                ##### MAIN LOOP #####


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
#####MAIN FUNCTION#####
#######################


#####CALL#####
def main():
    xcon = PIcontroller() #init for each axis. One of these isn't needed
    ycon = PIcontroller() #as gravity restrains the motion, but I won't know which it is until 
    zcon = PIcontroller() #I can test
    consolebrick()

    rm = pyvisa.ResourceManager() # init Resource Manager
    g = rm.list_resources() # list all ports. Only select from the ones that aren't system default ("ASRL")

    print("available devices:")
    for i in g:
      print(i + '\n')

    addrs = [] #ports for initializing devices

    print('pick n \n') # pick how many power supplies you want
    numadd = input('n:\n') # 1 sphere  -> 3, # 2 sphere -> 6
    for i in range(int(numadd)):
        addrs.append(g[i])

    ## init vectors
    VectorWrite(float(input("setpoint i: ")), float(input("setpoint j: ")), float(input("setpoint k: ")), False)
    VectorWrite(ax, ay, az, True)

    #####BLUETOOTH LE#####
    addresses = ['b9:e9:78:3f:10:da','9e:9d:53:fa:dc:16']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(addresses))

#####CALL#####


if __name__ == "__main__":
    main()

