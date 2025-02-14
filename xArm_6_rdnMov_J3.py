import csv
import time
import random
from xarm.wrapper import XArmAPI

# Parameter
ip = '10.2.33.190'  # xArm6 IP DC BOX
move_duration = 270  # # total duration of logging = move_duration + cooldown_dration
cooldown_duration = 30  # Cooldown in secs
repetitions = 7  # No. of repetitions = No. of CSV files
sampling_time = 0.5  # 2 Hz sampling rate
joint_id = 1  # joint DUT, joint number, starting from 0 (joint_id = 2 = joint #3) TEST
joint_3_id = 2  # joint #3 set angle
angle_min, angle_max = -105, 95  # angle range TEST
angle_3 = -180 # set angle for joint #3
speed = 50 # speed in °/s
"""set random speed, WIP"""
# speed_min, speed_max = 10, 30   # speed range
filename_template = "{iteration}_xArm6Log_{move_duration}_{cooldown_duration}_{angle_min}_{angle_max}_{speed}_j2.csv"
# connect/init
arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)
arm.move_gohome(wait=True)

def move_joint_to_angle():
    """Moves the 3rd joint to a specific angle"""
    print(f"Move Joint {joint_3_id + 1} to {angle_max:.2f}°")
    angles = arm.get_servo_angle()[1]  # get current angles
    angles[joint_3_id] = angle_3  # only change 3rd joint 
    arm.set_servo_angle(angle=angles, speed=speed, wait=True)

def move_joint_to_random_angle():
    """Moves the 2nd joint randomly between angle range"""
    random_angle = random.uniform(angle_min, angle_max)
    print(f"Move Joint {joint_id + 1} to {random_angle:.2f}°")
    angles = arm.get_servo_angle()[1]  # get current angles
    angles[joint_id] = random_angle  # only change 2nd joint TEST
    arm.set_servo_angle(angle=angles, speed=speed, wait=True)
    
def move_joint_to_zero():
    """Set 2nd joint to 0° for cooling"""
    print(f"Set joint {joint_id + 1} to 0°")
    angles = arm.get_servo_angle()[1]
    angles[joint_id] = 0   # degrees
    arm.set_servo_angle(angle=angles, speed=speed, wait=True)

def log_data(filename, duration):
    """Get sensor date and store in CSV files"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time (s)", "Pos_0", "Pos_1", "Pos_2", "Pos_3", "Pos_4", "Pos_5", "Pos_6", 
                             "Temp_0", "Temp_1", "Temp_2", "Temp_3", "Temp_4", "Temp_5", "Temp_6", 
                             "Torque_0", "Torque_1", "Torque_2", "Torque_3", "Torque_4", "Torque_5", "Torque_6",
                             "Current_0", "Current_1", "Current_2", "Current_3", "Current_4", "Current_5", "Current_6",
                             "Velocity_0", "Velocity_1", "Velocity_2", "Velocity_3", "Velocity_4", "Velocity_5", "Velocity_6",  # column names
                             "Tool_X", "Tool_Y", "Tool_Z", "Tool_Roll", "Tool_Pitch", "Tool_Yaw"])
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            # positions = arm.get_servo_angle(is_radian=False)
            positions = arm.angles
            temps = arm.temperatures
            torques = arm.joints_torque
            currents = arm.currents
            velocities = arm.realtime_joint_speeds
            # velocities = [velocities_value] * 7
            tool_position = arm.position  # X, Y, Z, Roll, Pitch, Yaw
            writer.writerow([elapsed_time] + positions + temps + torques + currents + velocities + tool_position)

            
            time.sleep(sampling_time)

def main():
    for iteration in range(repetitions):
        print(f"\n--- Repetition {iteration + 1}/{repetitions} ---")
        filename = filename_template.format(iteration=iteration, move_duration=move_duration, cooldown_duration=cooldown_duration, angle_min=angle_min, angle_max=angle_max, speed=speed)
        
        # logging in separate thread
        import threading
        log_thread = threading.Thread(target=log_data, args=(filename, move_duration + cooldown_duration))
        log_thread.start()
        
        time.sleep(1)  # pause before movement

        # Random joint movement according to duration, first move joint #3 to -180 for strech position
        move_joint_to_angle()
        start_time = time.time()
        while time.time() - start_time < move_duration:
            move_joint_to_random_angle()
            time.sleep(0.5)  # add pause between movements
        
        # set joint #3 to 0°
        move_joint_to_zero()
        time.sleep(cooldown_duration)

        # wait end of logging thread
        log_thread.join()
        print(f"Iteration {iteration + 1} finished, data stored in {filename}")
    
    arm.move_gohome(wait=True)
    arm.disconnect()

if __name__ == "__main__":
    main()
