# Imported Python Transfer Function
import sensor_msgs.msg
from hbp_nrp_excontrol.logs import clientLogger
import rospy
from gazebo_msgs.srv import GetModelState
from std_msgs.msg import String

@nrp.MapRobotSubscriber("position", Topic('/gazebo/model_states', gazebo_msgs.msg.ModelStates))
@nrp.MapSpikeSource("input_neuron_0", nrp.brain.input_neurons[0], nrp.dc_source)
@nrp.MapSpikeSource("input_neuron_1", nrp.brain.input_neurons[1], nrp.dc_source)
@nrp.MapVariable("service", initial_value=rospy.ServiceProxy('/gazebo/get_model_state', GetModelState, persistent=True))
@nrp.MapVariable("robot_index", global_key="robot_index", initial_value=None)
@nrp.MapVariable("already_triggered", initial_value=False, scope=nrp.GLOBAL)
@nrp.MapVariable("reset_start_position", scope=nrp.GLOBAL)
@nrp.MapVariable("distance", initial_value=0., scope=nrp.GLOBAL)
@nrp.MapVariable("distance_threshold_for_input_start", scope=nrp.GLOBAL)
@nrp.Robot2Neuron()
def input(t, position, input_neuron_0, input_neuron_1, service, robot_index, already_triggered, reset_start_position, distance, distance_threshold_for_input_start):
    import math
    import sys
    # TODO: Wenn State_communicator nicht mehr "preparing" ist fange an zu arbeiten
    #if state.value != None:
        #clientLogger.info(state.value)
    if not isinstance(position.value, type(None)):

        # determine if previously set robot index has changed
        if robot_index.value is not None:

            # if the value is invalid, reset the index below
            if robot_index.value >= len(position.value.name) or position.value.name[robot_index.value] != 'robot':
                robot_index.value = None

        # robot index is invalid, find and set it
        if robot_index.value is None:

            # 'robot' is guaranteed by the NRP, if not found raise error
            robot_index.value = position.value.name.index('robot')

        current_ball_state = service.value("ball", "world")

        # robot position is: position.value.pose[robot_index.value].position
        # ball position is: current_ball_state.pose.position
        # if  x, y and z are 0 the ball is not spawned so we don't calculate a new value
        if current_ball_state.pose.position.x != 0 and current_ball_state.pose.position.y != 0 and current_ball_state.pose.position.z != 0:
            distance.value = math.sqrt(math.pow((position.value.pose[robot_index.value].position.x - current_ball_state.pose.position.x), 2) + math.pow((position.value.pose[robot_index.value].position.y - current_ball_state.pose.position.y), 2) + math.pow((position.value.pose[robot_index.value].position.z - current_ball_state.pose.position.z), 2))
            
        # distance at ball spawn is 5.4
        # at the beginning there is no ball so distance won't be calculated. We set it so the NRP don't throw an error
        if distance.value is None:
            distance.value = 5
        # the new way where the input neuron fires continously while the ball is near enough
        if distance.value < distance_threshold_for_input_start.value:
            if distance.value == 0.:
                input_neuron_0.amplitude = sys.float_info.max
            else: 
                input_neuron_0.amplitude = 1. / distance.value
            input_neuron_1.amplitude = 1.
        else:
            input_neuron_0.amplitude = 0.
            input_neuron_1.amplitude = 0.

            # the old way where the input neuron fires one time if the ball gets near enough
            #if distance.value < distance_threshold_for_input_start.value:
                #if already_triggered.value == False:
                    #input_neurons.amplitude = 100.
                    #already_triggered.value = True
                #else: 
                    #input_neurons.amplitude = 0.
            #if distance.value > distance_threshold_for_input_start.value:
                #input_neurons.amplitude = 0.
                #if already_triggered.value == True:
                    #already_triggered.value = False
                    ##clientLogger.info('Reset input')
                    #reset_start_position.value = True