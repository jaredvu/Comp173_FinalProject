#
# San Diego Zoo Synchronization
# Jared Vu
#
import threading
from threading import*

class Car(object):
    def __init__(self):
        self.status = 0 #Status of car 0 is free, 1 occupied
        self.numRides = 0 #Number of rides car has given. Gas up at 5
        self.visitor = 0 #Visitor Number

class thread_arguments(object):
    def __init__(self, M, N, T, K):
        self.M = M
        self.N = N
        self.T = T
        self.K = K

#Global Variabls
ARGS = []
M = 0
N = 0
T = 0
K = 0
visitors = None
cars = None
pumps = None
s1 = None
s2 = None
carsServiced = 0
firstRun = True

def readIn(fileName):
    file = open(fileName, 'r')
    r = file.readlines()
    for line in r:
        argument = line.split(",")
        data = thread_arguments(int(argument[0]),int(argument[1]),int(argument[2]),int(argument[3]))
        ARGS.append(data)


def main():
    global M,N,T,K,visitors,cars,pumps,s1,s2
    for i in range(len(ARGS)):
        if ARGS[i].M == 0:
            break
        else:
            print('\nStarting Run #%d'%(i+1))
            print('---------------------\n')
            #Initialization
            M = ARGS[i].M
            N = ARGS[i].N
            T = ARGS[i].T
            K = ARGS[i].K
            visitors = [0 for i in range(M)]
            cars = [Car() for i in range(N)]
            pumps = [0 for i in range(K)]
            s1 = threading.BoundedSemaphore(N)
            s2 = threading.BoundedSemaphore(K)

            #Start the master Thread
            master = Thread(target = car_thr)
            master.start()
            master.join()
        print('\n---------------------\n')
    print('Finished all runs!')

#Checking for remaining cars/ visitor functions
def visitorsLeft():
    global visitors,M
    numVisitors = 0
    for i in range(M):
        if visitors[i] == 0:
            numVisitors += 1
    return numVisitors

def carsLeft():
    global cars,N
    numCars = 0
    for i in range(N):
        if cars[i].numRides >= 5:
            numCars += 1
    return numCars

#Thread Functions
def car_thr():
    global firstRun,visitors,cars
    firstRun = True
    currVisitor = 0

    #Run while there are visitors left
    while visitorsLeft()>0:
        #Assign numRides to 5 for all cars so they have to start at the gas station
        if firstRun is True:
            for i in range(N):
                cars[i].numRides = 5
        else:
            drivingCars = 0
            for i in range(N):
                if cars[i].numRides < 5 and cars[i].status == 0 and firstRun == False:
                    if currVisitor < M:
                        #Visitor has been given car. Car is now occupied. Number of rides car has given is incremented
                        #Increment number of cars currently driving
                        visitors[currVisitor] = 1
                        s1.acquire()
                        cars[i].status = 1
                        cars[i].numRides += 1
                        cars[i].visitor = currVisitor+1
                        drivingCars += 1
                        print('[CAR] Visitor %d is riding in car %d. Total cars giving rides: %d'%(currVisitor+1,i+1,drivingCars))
                        currVisitor += 1
            #start the visitor process
            visProcess = Thread(target = vis_thr)
            visProcess.start()
            visProcess.join()
        #start the gas process
        gasProcess = Thread(target = gas_thr)
        gasProcess.start()
        gasProcess.join()

def vis_thr():
    global s1,cars
    #Ride Timer
    rideTimer = 0
    while(rideTimer < T):
        rideTimer += 1
    #Release visitor from car
    for i in range(N):
        if cars[i].status == 1:
            s1.release()
            cars[i].status = 0
            print('[VIS] Visitor %d returned. Total visitors waiting: %d'%(cars[i].visitor,visitorsLeft()))

def gas_thr():
    global carsServiced,firstRun,s2,pumps
    queue = carsLeft()
    queue1 = queue
    if carsServiced >= 150:
        truckTimer = 0

        #Gas Truck called
        while truckTimer < 15:
            print('[GAS] Gas truck is refilling station')
            truckTimer+=1
        carsServiced = 0
        print('[GAS] Gas truck has finished refilling station')

    while queue > 0:
        if firstRun is True:
            firstRun = False

        #check to see if there are free pumps, then put cars at them
        for i in range(K):
            if(pumps[i] == 0 and queue > 0):
                s2.acquire()
                pumps[i] = 1
                carsServiced += 1
                queue-=1
                print('[GAS] Pump %d occupied. Number of cars waiting to gas: %d'%(i+1,queue))

        #Fueling time
        fuelTime = 0
        while(fuelTime < 3):
            fuelTime+=1

        #Release the pump
        for i in range(K):
            if pumps[i] == 1:
                s2.release()
                pumps[i] = 0
                queue1-=1
                print('[GAS] Pump %d is free. Number of cars fueling: %d'%(i+1, queue1-queue))
        #Set all of numRides for the cars to 0.
        for i in range(N):
            if cars[i].numRides >= 5:
                cars[i].numRides = 0

if __name__ == '__main__':
    z = input('Enter the name of a data file to read in: ')
    readIn(z)
    main()