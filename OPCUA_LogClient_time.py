import asyncio
import logging
import threading
import time
import csv
from asyncua import Client, ua

# Function for running async Functions in multithreading
def asyncThreads(function, client, name):
    asyncio.run(function(client, name))

async def opcua_get_temperature(client, name):
    # Connect to OPC UA server
    async with client:
        print("Connecting to: " + name)

        # Discover all Nodes and Variables
        AllNodesVar = await client.nodes.root.get_child(
            ["0:Objects", "1:AllNodeIDs"]
        )
        buffer = await AllNodesVar.read_value()
        AllNodeslist = buffer.split("#")[:-1]
        print(AllNodeslist)

          #Add Positions
        VarList = []
        for var in AllNodeslist:
            if "position" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                print(VarList[-1])

        #Add Temperatures
        for var in AllNodeslist:
            if "temperature_motor" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                print(VarList[-1])

        #Add Torques
        for var in AllNodeslist:
            if "torque" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                print(VarList[-1])
        
       # Add Motor currents, excluding base.arm_current
        for var in AllNodeslist:
            if "current" in var and "arm_current" not in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                print(VarList[-1])
        
        #Add Velocities
        for var in AllNodeslist:
            if "velocity" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                print(VarList[-1])

        # Create CSV
        filename = f"{1}_KinovaLog_j6_periodic_weight.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(["Time (s)", "Pos_0", "Pos_1", "Pos_2", "Pos_3", "Pos_4", "Pos_5", "Pos_6", 
                             "Temp_0", "Temp_1", "Temp_2", "Temp_3", "Temp_4", "Temp_5", "Temp_6", 
                             "Torque_0", "Torque_1", "Torque_2", "Torque_3", "Torque_4", "Torque_5", "Torque_6",
                             "Current_0", "Current_1", "Current_2", "Current_3", "Current_4", "Current_5", "Current_6",
                             "Velocity_0", "Velocity_1", "Velocity_2", "Velocity_3", "Velocity_4", "Velocity_5", "Velocity_6"])
        
        # Get data from OPC UA server:
        start_time = time.time()  # Start time for calculating elapsed time
        while True:
            val = await client.read_values(VarList[:])
            
            # Debugging
            print(f"Values to write: {val}")

            # Check 
            if len(val) == 35:  # expected 35 values
                elapsed_time = time.time() - start_time  # Calculate elapsed time
                with open(filename, 'a', newline='') as f:
                    writer = csv.writer(f, dialect='excel')
                    writer.writerow([elapsed_time] + val)  # Add elapsed time as the first element
            else:
                print(f"Unexpected number of values: {len(val)}")

            await asyncio.sleep(0.5)

print("Starting OPCUA Client")
client = Client("opc.tcp://192.168.0.101:4840")  # Pi IP address
print("Client Created")
my_thread = threading.Thread(target=asyncThreads, args=(opcua_get_temperature, client, "Kinova"))
my_thread.start()
