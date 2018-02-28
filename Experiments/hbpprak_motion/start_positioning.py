@nrp.MapRobotPublisher('joint_2', Topic('/robot/hollie_real_left_arm_2_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_3', Topic('/robot/hollie_real_left_arm_3_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_4', Topic('/robot/hollie_real_left_arm_4_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_6', Topic('/robot/hollie_real_left_arm_6_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapVariable("reset_start_position", initial_value=True, scope=nrp.GLOBAL)
@nrp.Robot2Neuron()

def start_positioning(t, joint_2, joint_3, joint_4, joint_6, reset_start_position):
    if reset_start_position.value:
        #log the first timestep (20ms), each couple of seconds
        joint_2.send_message(std_msgs.msg.Float64(1.0))
        joint_3.send_message(std_msgs.msg.Float64(-1.0))
        joint_4.send_message(std_msgs.msg.Float64(1.0))
        joint_6.send_message(std_msgs.msg.Float64(0.0))
        reset_start_position.value = False