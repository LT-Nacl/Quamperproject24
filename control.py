import pyvisa # only run this after you are plugged into the power supplies ... NI-VISA and pyvisa install required, ask Alex
import time 

def consolebrick(): # just for formatting
    print('\n')
    a = '#'
    for i in range(5):
        print(a*30)
    print('\n')

consolebrick()

rm = pyvisa.ResourceManager() # init Resource Manager
g = rm.list_resources() # list all ports. Only select from the ones that aren't system default ("ASRL")

print("available devices:")
for i in g:
    print(i + '\n')

addrs = [] #ports for initializing devices

print('pick n \n') # pick how many power supplies you want
numadd = input('n:\n') # 1 sphere  -> 3, # 2 sphere -> 6

print('pick list index(s) (see device list): \n') # manually add addresses (0 index)
for i in range(int(numadd)):
    addrs.append(g[int(input("index:\n"))])

consolebrick()

print("addresses selected:\n")
devices = []

for i in addrs: #initialize each of the devices from the stored ports, add it to devices list
    print(i)
    devices.append(rm.open_resource(i))

consolebrick()

#ts finna get messy

def powersup(voltage, currentlim, time, device): # time is redundant at pat's request, easily reimplimented
    raw = ('*RST#'
    ':SOUR:FUNC VOLT#'
    f':SOUR:VOLT {voltage}#'
    f':SOUR:VOLT:ILIM {currentlim}#'
    f':TRIG:LOAD "SimpleLoop", {time}, 1#'
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

# n = 0
# vals = []
#while n < len(devices): # old device by device setup, readd if you want
 #   print('device #' + str(n + 1) + ":\n")
    #v = float(input("voltage: \n"))
    #i = float(input("current: \n"))
   # t = float(input("seconds: \n"))
  #  vals.append([v, i, t])
   # n+=1
#consolebrick()
#n = 0
#while n < len(devices):
 #   powersup(vals[n][0],vals[n][1],vals[n][2],devices[n])
  #  print('device ' + str(n + 1) + ' initiated!\n')
#    n+=1


while True: #I am about to entirely redo this segment to work with vectors, and change current vs voltage
    x = input("update: [exit,deviceindex,voltage]")
    parsed = x.split(",")
    if int(parsed[0]) == 1:
        devices[int(parsed[1])].write(':OUTP OFF')
    else:
        powersup(float(parsed[2]),1,1,devices[int(parsed[1])])

            #for those unfortunate enough to work with my code:
            #When testing the update, follow to format:

            #   exit?[INT],device number[INT],voltage[FLOAT]

            #Do not skip exit?, if you want it to stay on, just put something else

                
