import asyncio
import logging
import threading
import time
import csv
from asyncua import Client
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.messages import Base_pb2
import random
import os
import sys

# Parameter
move_duration = 20 # = duration of recording in secs
cooldown_duration = 10  # Cooldown in secs
repetitions = 3  # No. of repetitions = No. of CSV files
OPCUA_Server_IP = "opc.tcp://192.168.0.102:4840"
filename_template = "{iteration}_KinovaLog_{move_duration}_{cooldown_duration}_API.csv"
joint_id = 3    # joint number, starting from 0 (joint_id = 3 = joint #4)
angle_min = 45  # angle range 
angle_max = 90  

# Random Joint configuration
def move_joint_to_random_angle(base, joint_id=3, angle_min=angle_min, angle_max=angle_max):
    random_angle = random.uniform(angle_min, angle_max)
    print(f"Moving joint {joint_id+1} to random angle: {random_angle:.2f}°...")
    action = Base_pb2.Action()
    action.name = f"Random Joint {joint_id} Movement"
    actuator_count = base.GetActuatorCount().count

    for joint in range(actuator_count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint
        joint_angle.value = random_angle if joint == joint_id else 0

    e = threading.Event()
    base.OnNotificationActionTopic(check_for_end_or_abort(e), Base_pb2.NotificationOptions())
    base.ExecuteAction(action)
    e.wait(20)

# set joint #4 to 0°
def move_joint_to_zero(base, joint_id=3):
    print(f"Moving joint {joint_id+1} to 0°...")
    action = Base_pb2.Action()
    action.name = f"Set Joint {joint_id} to 0°"
    actuator_count = base.GetActuatorCount().count

    for joint in range(actuator_count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint
        joint_angle.value = 0 if joint == joint_id else 0

    e = threading.Event()
    base.OnNotificationActionTopic(check_for_end_or_abort(e), Base_pb2.NotificationOptions())
    base.ExecuteAction(action)
    e.wait(20)

# OPC-Client and logging
async def opcua_log_data(client, iteration):
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

        filename = filename_template.format(iteration=iteration, move_duration=move_duration, cooldown_duration=cooldown_duration)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(["Time (s)", "Pos_0", "Pos_1", "Pos_2", "Pos_3", "Pos_4", "Pos_5", "Pos_6", 
                             "Temp_0", "Temp_1", "Temp_2", "Temp_3", "Temp_4", "Temp_5", "Temp_6", 
                             "Torque_0", "Torque_1", "Torque_2", "Torque_3", "Torque_4", "Torque_5", "Torque_6",
                             "Current_0", "Current_1", "Current_2", "Current_3", "Current_4", "Current_5", "Current_6",
                             "Velocity_0", "Velocity_1", "Velocity_2", "Velocity_3", "Velocity_4", "Velocity_5", "Velocity_6"])  # column names

            start_time = time.time()
            while time.time() - start_time < move_duration:
                elapsed_time = time.time() - start_time
                val = await client.read_values(VarList[:])
                writer.writerow([elapsed_time] + val)
                await asyncio.sleep(0.5)  # 2 Hz sampling rate

def check_for_end_or_abort(e):
    def check(notification, e=e):
        #print("EVENT: " + Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event in [Base_pb2.ACTION_END, Base_pb2.ACTION_ABORT]:
            e.set()
    return check

def main():
    # init OPC UA Client
    opcua_client = Client(OPCUA_Server_IP)

    # connect to Kinova via utilities.py -> set Kinova robot IP here
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import utilities
    args = utilities.parseConnectionArguments()

    with utilities.DeviceConnection.createTcpConnection(args) as router:
        base = BaseClient(router)

        for iteration in range(repetitions):
            print(f"\n--- Repetition {iteration + 1}/{repetitions} ---")

            # OPC UA logging in separate thread
            opcua_thread = threading.Thread(target=asyncio.run, args=(opcua_log_data(opcua_client, iteration),))
            opcua_thread.start()

            # Random joint movement according to duration
            start_time = time.time()
            while time.time() - start_time < move_duration:
                move_joint_to_random_angle(base)

            # Set joint #4 to 0°
            move_joint_to_zero(base)
            time.sleep(cooldown_duration)

            # Stop logging
            if opcua_thread.is_alive():
                opcua_thread.join()

            print(f"Iteration {iteration + 1} finished, data stored.")

if __name__ == "__main__":
    main()
