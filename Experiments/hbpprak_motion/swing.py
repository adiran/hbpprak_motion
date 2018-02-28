@nrp.MapSpikeSink("output_neuron_0", nrp.brain.output_neurons[0], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_1", nrp.brain.output_neurons[1], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_2", nrp.brain.output_neurons[2], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_3", nrp.brain.output_neurons[3], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_4", nrp.brain.output_neurons[4], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_5", nrp.brain.output_neurons[5], nrp.leaky_integrator_alpha)
@nrp.MapSpikeSink("output_neuron_6", nrp.brain.output_neurons[6], nrp.leaky_integrator_alpha)
@nrp.MapRobotPublisher('joint_0', Topic('/robot/hollie_real_left_arm_0_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_1', Topic('/robot/hollie_real_left_arm_1_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_2', Topic('/robot/hollie_real_left_arm_2_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_3', Topic('/robot/hollie_real_left_arm_3_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_4', Topic('/robot/hollie_real_left_arm_4_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_5', Topic('/robot/hollie_real_left_arm_5_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapRobotPublisher('joint_6', Topic('/robot/hollie_real_left_arm_6_joint/cmd_pos', std_msgs.msg.Float64))
@nrp.MapVariable("already_swung", initial_value=False)
@nrp.MapVariable("distance", initial_value=0., scope=nrp.GLOBAL)
@nrp.MapVariable("distance_threshold_for_input_start", scope=nrp.GLOBAL)
@nrp.MapVariable("reset_start_position", scope=nrp.GLOBAL)
@nrp.Neuron2Robot()
def swing(t, output_neuron_0, output_neuron_1, output_neuron_2, output_neuron_3, output_neuron_4, output_neuron_5, output_neuron_6, joint_0, joint_1, joint_2, joint_3, joint_4, joint_5, joint_6, already_swung, distance, distance_threshold_for_input_start, reset_start_position):
    import math
    # we only swing if the distance is short enough
    if distance.value < distance_threshold_for_input_start.value:
        joint_0_value = output_neuron_0.voltage % math.pi
        joint_1_value = output_neuron_1.voltage % math.pi
        joint_2_value = output_neuron_2.voltage % math.pi
        joint_3_value = output_neuron_3.voltage % math.pi
        joint_4_value = output_neuron_4.voltage % math.pi
        joint_5_value = output_neuron_5.voltage % math.pi
        joint_6_value = output_neuron_6.voltage % math.pi
    else:
        joint_0_value = 0.
        joint_1_value = 0.
        joint_2_value = 0.
        joint_3_value = 0.
        joint_4_value = 0.
        joint_5_value = 0.
        joint_6_value = 0.
    joint_0.send_message(std_msgs.msg.Float64(joint_0_value))
    joint_1.send_message(std_msgs.msg.Float64(1. - joint_1_value))
    joint_2.send_message(std_msgs.msg.Float64(1. + joint_2_value))
    joint_3.send_message(std_msgs.msg.Float64(-1. + joint_3_value))
    joint_4.send_message(std_msgs.msg.Float64(1. + joint_4_value))
    joint_5.send_message(std_msgs.msg.Float64(joint_5_value))
    joint_6.send_message(std_msgs.msg.Float64(joint_6_value))