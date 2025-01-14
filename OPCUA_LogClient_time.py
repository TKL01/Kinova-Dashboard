###
# This App consists of 2 parts:
# (1) It connects to an OPC-UA server to collect data from a Kinova Gen3 7 DOF robot (joint positions, temperatures, torques, currents and velocities)
#     and stores the data in CSV files. 
#     There is an option to stop the data collection after a specific time (uncomment to activate)

# (2) This App connects to the Kinova Gen3 7 DOF robot and generates random joint (4th joint) movements between 2 specific degrees in joint space.
#     The Kortex API (v2.6.0) and additional instructions can be found here: https://github.com/Kinovarobotics/Kinova-kortex2_Gen3_G3L
#     It is required to set the robots IP adress in the utilities.py file. 
# 
#     OPC-UA server created by FG
#     OPC-UA client and csv data structure created by PA
#     Extensions to the client and data structure, random joint movements created by TKL
###


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
        filename = f"{1}_KinovaLog_0_0_90_API.csv"
        #filename = f"{1}_KinovaLog_fast_test.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(["Time (s)", "Pos_0", "Pos_1", "Pos_2", "Pos_3", "Pos_4", "Pos_5", "Pos_6", 
                             "Temp_0", "Temp_1", "Temp_2", "Temp_3", "Temp_4", "Temp_5", "Temp_6", 
                             "Torque_0", "Torque_1", "Torque_2", "Torque_3", "Torque_4", "Torque_5", "Torque_6",
                             "Current_0", "Current_1", "Current_2", "Current_3", "Current_4", "Current_5", "Current_6",
                             "Velocity_0", "Velocity_1", "Velocity_2", "Velocity_3", "Velocity_4", "Velocity_5", "Velocity_6"])
            
#########################Set a time############################################################################################        
#        # get data from OPC UA server:
#         start_time = time.time()  # start time for calculating elapsed time
#         seconds = 300 
#         while True:
#             elapsed_time = time.time() - start_time  # calculate elapsed time
#             if elapsed_time > seconds:  # stop after x secs
#                 #print("Stopping data collection after" + seconds + "s")
#                 break
            
#             val = await client.read_values(VarList[:])
            
            
#             print(f"Values to write: {val}")

#             # check 
#             if len(val) == 35:  # expected 35 values
#                 with open(filename, 'a', newline='') as f:
#                     writer = csv.writer(f, dialect='excel')
#                     writer.writerow([elapsed_time] + val)  # add elapsed time as the first element
#             else:
#                 print(f"Unexpected number of values: {len(val)}")

#             await asyncio.sleep(0.5)  # 2 hz sampling rate

# print("Starting OPCUA Client")
# client = Client("opc.tcp://192.168.0.102:4840")  # always check Pi IP address
# print("Client Created")
# my_thread = threading.Thread(target=asyncThreads, args=(opcua_get_temperature, client, "Kinova"))
# my_thread.start()
####################################################################################################################################

#########################Without a specific time############################################################################################  
#get data from OPC UA server:
        start_time = time.time()  # Start time for calculating elapsed time
        while True:
            val = await client.read_values(VarList[:])
            
            # Debugging
            print(f"Values to write: {val}")

            # Check 
            if len(val) == 35:  # expected 35 values
                elapsed_time = time.time() - start_time  # calculate elapsed time
                with open(filename, 'a', newline='') as f:
                    writer = csv.writer(f, dialect='excel')
                    writer.writerow([elapsed_time] + val)  # add elapsed time as the first element
            else:
                print(f"Unexpected number of values: {len(val)}")

            await asyncio.sleep(0.5)  # 2 hz sampling rate not enough?
            # TO-DO sample 2 mins only, add weight, increase vel.:

print("Starting OPCUA Client")
client = Client("opc.tcp://192.168.0.102:4840")  # Pi IP address
print("Client Created")
my_thread = threading.Thread(target=asyncThreads, args=(opcua_get_temperature, client, "Kinova"))
my_thread.start()
####################################################################################################################################



import sys
import os
import random
import threading
import time

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 20

# Actuator speed (deg/s)
# SPEED = 20.0

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications

    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e=e):
        print("EVENT: " + Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check

def move_joint_to_random_angle(base, joint_id=3, angle_min=45, angle_max=90):           # set here for check
    """Moves a specific joint to a random angle within the specified range."""
    # Make sure the arm is in Single Level Servoing mode
    # base_servo_mode = Base_pb2.ServoingModeInformation()
    # base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    # base.SetServoingMode(base_servo_mode)
    random_angle = random.uniform(angle_min, angle_max)
    print(f"Moving joint {joint_id} to a random angle: {random_angle:.2f}°...")
    
    action = Base_pb2.Action()
    action.name = "Random Joint 4 (joint_id = 3) Movement"
    action.application_data = ""

    actuator_count = base.GetActuatorCount().count      # 7

    # set the target angle for the specified joint
    for joint in range(actuator_count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint
        joint_angle.value = random_angle if joint == joint_id else 0

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    base.ExecuteAction(action)

    print("Waiting for movement to finish...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print(f"Joint {joint_id} successfully moved to {random_angle:.2f}°.")
    else:
        print("Timeout during joint movement.")
    return finished

def main():
    # Import the utilities helper module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities

    # Parse arguments
    args = utilities.parseConnectionArguments()

    # Create connection to the device and get the router
    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)

        # Infinite loop for random movements
        try:
            while True:
                success = move_joint_to_random_angle(base, joint_id=3, angle_min=0, angle_max=90)
                if not success:
                    print("Error during movement. Exiting loop.")
                    break
                
                time.sleep(1)  # delay between movements
        except KeyboardInterrupt:
            print("\nStopped by user.")

if __name__ == "__main__":
    exit(main())
