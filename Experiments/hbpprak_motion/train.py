import numpy as np
@nrp.MapVariable('distance', scope=nrp.GLOBAL)
@nrp.MapVariable('last_distance_sum', initial_value=0.)
@nrp.MapVariable('distance_array')
@nrp.MapVariable('current_distance_sum', initial_value=0.)
@nrp.MapVariable('last_hit_counter', initial_value=0)
@nrp.MapVariable('current_hit_counter', initial_value=0)
@nrp.MapVariable('last_weights', initial_value=[[ 1., 1., 1., 1., 1., 1., 1.], [ 1., 1., 1., 1., 1., 1., 1.]])
@nrp.MapRobotSubscriber("state_subscriber", Topic('/State_communicator', String))
@nrp.MapRobotPublisher("state_publisher", Topic('/State_communicator', String))
@nrp.MapVariable('start_with_weights', initial_value=True)
# the following two Variables should have equal initial_value
@nrp.MapVariable('distance_threshold_for_input_start', initial_value=4.5, scope=nrp.GLOBAL)
@nrp.MapVariable('last_distance_threshold_for_input_start', initial_value=4.5, scope=nrp.GLOBAL)
# if false the experiment will not change the weights of the brain
@nrp.MapVariable('training', initial_value=True)
# counts the experiment runs per training step
@nrp.MapVariable('experiment_runs_counter', initial_value=0)
# we want a robust movement so we can cancle the training if the racket does not hit the ball (after we had a training step where it has hit it every time)
@nrp.MapVariable('has_hit_every_time', initial_value=False)
@nrp.MapCSVRecorder("logger", filename="results.csv", headers=["Realtime", "Experimenttime", "distance_threshold_for_input_start", "weights", "distance_array", "distance_sum", "hit_counter", "keep new weights"])
@nrp.Neuron2Robot()
def train(t, distance, last_distance_sum, distance_array, current_distance_sum, last_hit_counter, current_hit_counter, last_weights, state_subscriber, state_publisher, start_with_weights, distance_threshold_for_input_start, last_distance_threshold_for_input_start, training, experiment_runs_counter, has_hit_every_time, logger):
    import datetime
    import random
    if distance_array.value is None:
        distance_array.value = []
    # if start_with_weights is set, we set some weights to the brain. This could be weights you guessed or weights from a previous run
    if start_with_weights.value:
        initial_weights = np.array([[ 156.68351116, -82.92193666, 87.96451072, -117.85911876, -44.95404428, 92.71091689, -142.38430199], [ 208.44833995, 232.45617944, 73.02390528, 117.94190121, -33.16189514, -75.99892642, 0.65456941]])
        #initial_weights = np.array([[-3.18446158, 0.46332848, -1.19960841, 1.57664565, 1.32146154, 0.02485128, -5.17042701], [ 2.41336852, 3.44648413, 1.87506143, 1.76541807, -5.06323044, -1.26174709, -3.40507255]])
        distance_threshold_for_input_start.value = 3.291366556565804
        nrp.config.brain_root.connections.set(weight=initial_weights)
        last_weights.value = initial_weights
        last_distance_threshold_for_input_start.value = distance_threshold_for_input_start.value
        start_with_weights.value = False
        clientLogger.info("Set inital weights: " + str(last_weights.value))
    RUNNING = 'running'
    START_EVALUATING = 'start_eval'
    FINISH_EVALUATING = 'finish_eval'
    # a threshold so we only keep the new weights if the new distance is greater than the old distance + threshold
    distance_threshold = .1
    # we change each weight by a random number between -weight_changes and +weight_changes
    weight_changes = 1.
    # we change the distance_threshold_for_input_start by a random number between -distance_threshold_for_input_start_changes and +distance_threshold_for_input_start_changes
    distance_threshold_for_input_start_changes = 0.5
    # Number of weights that should be changed in one training. Maximum is 9
    weights_to_change = 7
    # possibility to change distance_threshold_for_input_start. The possibility is 1 to change_distance_treshold_possibility
    # e. g. if change_distance_treshold_possibility = 4 the possibility is 1:4
    # have to be > 0. Set to 1 to not change the distance_threshold_for_input_start
    change_distance_treshold_possibility = 8
    # the hitting of the ball is not very deterministic so we make more than one run in one training step
    # so we can see how robust the hitting is if we try to strike the ball as often as possible
    experiment_runs_per_training_step = 5

    if state_subscriber.value != None:
        #clientLogger.info(state_subscriber.value.data)
        if state_subscriber.value.data == START_EVALUATING:
            if training.value == True:
                experiment_runs_counter.value = experiment_runs_counter.value + 1
                clientLogger.advertise("Run " + str(experiment_runs_counter.value) + "/" + str(experiment_runs_per_training_step) + " - Distance: " + str(distance.value) + " m.")
                current_distance_sum.value = current_distance_sum.value + distance.value
                distance_array.value.append(distance.value)
                clientLogger.info(distance_array.value)
                # if the racket doesn't hit the ball it flies about 4.5 so if distance is greater 5.0 the ball was hit
                if distance.value > 5.:
                    current_hit_counter.value = current_hit_counter.value + 1
                # if we already hit the ball in every run in a training step we can abort the current training step if we don't hit the ball
                # we have to reset the weights and then change them again so we have a new training step
                elif has_hit_every_time.value == True:
                    experiment_runs_counter.value = 0
                    current_distance_sum.value = 0.
                    current_hit_counter.value = 0
                    distance_array.value = []
                    clientLogger.info("Doesn't hit the ball so we abort this training step")
                    current_weights = last_weights.value[:]
                    distance_threshold_for_input_start.value = last_distance_threshold_for_input_start.value
                    # change the weights
                    changed_indices = []
                    for i in range(weights_to_change):
                        index = random.randrange(len(current_weights) * len(current_weights[0]))
                        while index in changed_indices:
                            #clientLogger.info("Index was already changed")
                            index = random.randrange(len(current_weights) * len(current_weights[0]))
                        changed_indices.append(index)
                        position_number = index % len(current_weights[0])
                        array_number = index / len(current_weights[0])
                        change = random.uniform(-1*weight_changes, weight_changes)
                        #clientLogger.info("changed index " + str(index) + " that was " + str(current_weights[index]) + " by " + str(change))
                        current_weights[array_number][position_number] = current_weights[array_number][position_number] + change

                    change_distance_treshold = random.randrange(change_distance_treshold_possibility)
                    if change_distance_treshold == 1:
                        change = random.uniform(-1*distance_threshold_for_input_start_changes, distance_threshold_for_input_start_changes)
                        # clientLogger.info("changed distance_threshold_for_input_start that was " + str(distance_threshold_for_input_start.value) + " by " + str(change))
                        distance_threshold_for_input_start.value = distance_threshold_for_input_start.value + change

                    #clientLogger.info("changed the following indices: " + str(changed_indices))

                    # set the new weights

                    nrp.config.brain_root.connections.set(weight=current_weights)

                if experiment_runs_counter.value >= experiment_runs_per_training_step:
                    if current_hit_counter.value == experiment_runs_per_training_step:
                        has_hit_every_time.value = True
                    current_weights = nrp.config.brain_root.connections.get("weight", format="array")
                    # check if distance is greater than last time.
                    # if not we reset the weights to the old values
                    if current_distance_sum.value > (last_distance_sum.value + distance_threshold):
                        clientLogger.advertise("Succeeded to improve: " + str(current_distance_sum.value) + " m over all runs with " + str(current_hit_counter.value) + " hits.")
                        clientLogger.info("Ball flew further than last time: " + str(current_distance_sum.value) + " > (" + str(last_distance_sum.value) + " + " + str(distance_threshold) + ")")
                        logger.record_entry(datetime.datetime.now(), t, distance_threshold_for_input_start.value, current_weights, distance_array.value, current_distance_sum.value, current_hit_counter.value, "True")
                        last_distance_sum.value = current_distance_sum.value
                        last_hit_counter.value = current_hit_counter.value
                        last_weights.value = current_weights[:]
                        last_distance_threshold_for_input_start.value = distance_threshold_for_input_start.value
                    else:
                        clientLogger.advertise("Failed to improve: " + str(current_distance_sum.value) + " m over all runs with " + str(current_hit_counter.value) + " hits.")
                        clientLogger.info("Ball didn't flew further than last time: " + str(current_distance_sum.value) + " < (" + str(last_distance_sum.value) + " + " + str(distance_threshold) + ")")
                        logger.record_entry(datetime.datetime.now(), t, distance_threshold_for_input_start.value, current_weights, distance_array.value, current_distance_sum.value, current_hit_counter.value, "False")
                        current_weights = last_weights.value[:]
                        distance_threshold_for_input_start.value = last_distance_threshold_for_input_start.value
                        #clientLogger.info("reset weights: " + str(current_weights))
                    # reset counters
                    experiment_runs_counter.value = 0
                    current_distance_sum.value = 0.
                    current_hit_counter.value = 0
                    distance_array.value = []
                    # change the weights
                    changed_indices = []
                    for i in range(weights_to_change):
                        index = random.randrange(len(current_weights) * len(current_weights[0]))
                        while index in changed_indices:
                            #clientLogger.info("Index was already changed")
                            index = random.randrange(len(current_weights) * len(current_weights[0]))
                        changed_indices.append(index)
                        position_number = index % len(current_weights[0])
                        array_number = index / len(current_weights[0])
                        change = random.uniform(-1*weight_changes, weight_changes)
                        #clientLogger.info("changed index " + str(index) + " that was " + str(current_weights[index]) + " by " + str(change))
                        current_weights[array_number][position_number] = current_weights[array_number][position_number] + change

                    change_distance_treshold = random.randrange(change_distance_treshold_possibility)
                    if change_distance_treshold == 1:
                        change = random.uniform(-1*distance_threshold_for_input_start_changes, distance_threshold_for_input_start_changes)
                        # clientLogger.info("changed distance_threshold_for_input_start that was " + str(distance_threshold_for_input_start.value) + " by " + str(change))
                        distance_threshold_for_input_start.value = distance_threshold_for_input_start.value + change

                    #clientLogger.info("changed the following indices: " + str(changed_indices))

                    # set the new weights

                    nrp.config.brain_root.connections.set(weight=current_weights)

                    # Set distance greater than distance_threshold_for_input_start so the robot moves his hand to the starting position
                    distance.value = distance_threshold_for_input_start.value + 1.



                    # Easteregg because jacky said so
                    if random.random() < 0.001:
                        phrases = ["Unser Leben ist das Produkt unserer Gedanken. - Marcus Aurelius", "Das einzig Wichtige im Leben sind die Spuren der Liebe, die wir hinterlassen, wenn wir gehen. - Albert Schweitzer", "Das Schönste, was wir erleben können, ist das Geheimnisvolle. - Albert Einstein", "Die Summe unseres Lebens sind die Stunden, in denen wir liebten. - Wilhelm Busch", "Das Geheimnis eines glücklichen Lebens liegt in der Entsagung. - Mahatma Gandhi", "Ein Mensch, der für nichts zu sterben gewillt ist, verdient nicht zu leben. - Martin Luther King", "Was wäre das Leben, hätten wir nicht den Mut, etwas zu riskieren? - Vincent van Gogh", "Man merkt nie, was schon getan wurde, man sieht immer nur, was noch zu tun bleibt. - Marie Curie", "Leben, das ist das Allerseltenste in der Welt – die meisten Menschen existieren nur. - Oscar Wilde", "Es gibt ein erfülltes Leben trotz vieler unerfüllter Wünsche. - Dietrich Bonhoeffer", "Wer das Leben nicht schätzt, der verdient es nicht. - Leonardo da Vinci", "Die Menschen stolpern nicht über Berge, sondern über Maulwurfshügel. - Konfuzius", "Wer von seinem Tag nicht zwei Drittel für sich selbst hat, ist ein Sklave. - Friedrich Nietzsche", "Trenne dich nicht von deinen Illusionen. Wenn sie verschwunden sind, wirst du weiter existieren, aber aufgehört haben zu leben. - Mark Twain", "Einen Vorsprung im Leben hat, wer da anpackt, wo die anderen erst einmal reden. - John F. Kennedy", "trinkt bier, es ist sehr gut! - kai-UWE"]
                        phrase_position = random.randrange(len(phrases))
                        logger.record_entry("-1", "-1", "-1", "-1", "-1", "-1", "-1", phrases[phrase_position])

                # Change state_communicator so we restart the experiment
                state_publisher.send_message(std_msgs.msg.String(FINISH_EVALUATING))
                    
            else:
                clientLogger.advertise("Distance: " + str(distance.value) + " m.")
                state_publisher.send_message(std_msgs.msg.String(FINISH_EVALUATING))
                # Set distance greater than distance_threshold_for_input_start so the robot moves his hand to the starting position
                distance.value = distance_threshold_for_input_start.value + 1.
