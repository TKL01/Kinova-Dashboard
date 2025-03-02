import asyncio
import csv
import time
from asyncua import Client

OPCUA_Server_IP = "opc.tcp://192.168.0.106:4840" #raspberry pi opcua server ip
sampling_time = 0.5  # 2 Hz sampling rate

# OPC-Client and logging
async def opcua_log_data(client):
    async with client:
        print("Connecting to OPC UA server...")
        # read nodes and log data
        AllNodesVar = await client.nodes.root.get_child(["0:Objects", "1:AllNodeIDs"])
        buffer = await AllNodesVar.read_value()
        AllNodeslist = buffer.split("#")[:-1]

        # discover all Nodes and Variables
        AllNodesVar = await client.nodes.root.get_child(
            ["0:Objects", "1:AllNodeIDs"]
        )
        buffer = await AllNodesVar.read_value()
        AllNodeslist = buffer.split("#")[:-1]
        #print(AllNodeslist)

          #Add Positions
        VarList = []
        for var in AllNodeslist:
            if "position" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                #print(VarList[-1])

        #Add Temperatures
        for var in AllNodeslist:
            if "temperature_motor" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                #print(VarList[-1])

        #Add Torques
        for var in AllNodeslist:
            if "torque" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                #print(VarList[-1])
        
       # Add Motor currents, excluding base.arm_current
        for var in AllNodeslist:
            if "current" in var and "arm_current" not in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                #print(VarList[-1])
        
        #Add Velocities
        for var in AllNodeslist:
            if "velocity" in var:
                VarList.append(await client.nodes.root.get_child(
                    ["0:Objects", f"1:{var}"]
                ))
                #print(VarList[-1])
        
        filename = "KinovaLog_HoloLens_recording_3_3_j2.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(["Time (s)", "Pos_0", "Pos_1", "Pos_2", "Pos_3", "Pos_4", "Pos_5", "Pos_6", 
                             "Temp_0", "Temp_1", "Temp_2", "Temp_3", "Temp_4", "Temp_5", "Temp_6", 
                             "Torque_0", "Torque_1", "Torque_2", "Torque_3", "Torque_4", "Torque_5", "Torque_6",
                             "Current_0", "Current_1", "Current_2", "Current_3", "Current_4", "Current_5", "Current_6",
                             "Velocity_0", "Velocity_1", "Velocity_2", "Velocity_3", "Velocity_4", "Velocity_5", "Velocity_6"])  # column names
            
            start_time = time.time()
            while True:
                elapsed_time = time.time() - start_time
                val = await client.read_values(VarList[:])
                writer.writerow([elapsed_time] + val)
                await asyncio.sleep(sampling_time)

def main():
    opcua_client = Client(OPCUA_Server_IP)
    asyncio.run(opcua_log_data(opcua_client))

if __name__ == "__main__":
    main()
