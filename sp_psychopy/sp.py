"""Implement the Sampling Paradigm.

This is the main file.

see 'define_monitors.py' to first define a suitable monitor, which to then add
in the mywin = visual.Window call.

see 'define_payoff_distributions.py' for a closer look at the environments
where subjects have to make choices during this EEG experiment.

see 'define_ttl_triggers.py' for extensive comments on the meaning of the TTL
trigger values to be sent during the EEG experiment.

"""
import os
import os.path as op
import argparse

from psychopy import visual, event, core

import sp_psychopy
from sp_psychopy.utils import (get_fixation_stim, display_message,
                               display_outcome, inquire_action, log_data)
from sp_psychopy.define_payoff_distributions import payoff_dict_1
from sp_psychopy.define_ttl_triggers import (trig_begin_experiment,
                                             trig_msg_new_trial,
                                             trig_sample_onset,
                                             trig_left_choice,
                                             trig_right_choice,
                                             trig_final_choice,
                                             trig_mask_outcome,
                                             trig_outcome,
                                             trig_msg_zero_samples,
                                             trig_msg_final_choice,
                                             trig_choice_onset,
                                             trig_left_final_choice,
                                             trig_right_final_choice,
                                             trig_mask_final_outcome,
                                             trig_final_outcome,
                                             trig_end_experiment)

# Prepare for logging all experimental variables of interest
# Parse the subject ID
parser = argparse.ArgumentParser()
parser.add_argument('--sub_id', '-s', type=str, required=True)
args = parser.parse_args()

# BIDS data file name
fname = 'sub-{}_task-sp_events.tsv'.format(args.sub_id)

# Check directory is present and file name not yet used
data_dir = op.join(op.dirname(sp_psychopy.__file__), 'experiment_data')
if not op.exists(data_dir):
    os.mkdir(data_dir)

data_file = op.join(data_dir, fname)
if op.exists(data_file):
    raise OSError('A data file for {} '
                  'already exists: {}'.format(args.sub_id, data_file))

# Write an initial header to the tab separated log file
# For a description of the keys, see the "task-sp_events.json" file.
variables = ['onset', 'duration', 'action_type', 'action', 'outcome',
             'response_time', 'event_value']

with open(data_file, 'w') as fout:
    header = '\t'.join(variables)
    fout.write(header + '\n')


# Open connection to the serial port
class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


# For now, use a fake serial connection
ser = Fake_serial()

# Define monitor specific window object
mywin = visual.Window(size=[1280, 800],  # Size of window in pixels (x,y)
                      pos=[0, 0],  # X,Y position of window on screen
                      color=[0, 0, 0],  # Background color: RGB [-1,1]
                      fullscr=False,  # Fullscreen for better timing
                      monitor='p51',  # see monitor_definition.py
                      units='deg',
                      winType='pygame')  # Units being used for stimuli


# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(mywin)
fixation_stim_parts = [outer, horz, vert, inner]

# On which frame rate are we operating?
fps = int(round(mywin.getActualFrameRate()))
assert fps == 60

# Settings for the experimental flow
max_samples_overall = 10
max_samples_per_trial = 5

# Get ready to start the experiment. Start timing from next button press.
message = 'Welcome to the Sampling Paradigm task. Press any key to start.'
txt_stim = visual.TextStim(mywin, text=message, units='deg', height=1)
txt_stim.draw()
mywin.flip()
mywin.callOnFlip(ser.write, trig_begin_experiment)
event.waitKeys()
mywin.flip()
timer = core.Clock()
log_data(data_file, onset=timer.getTime(),
         event_value=trig_begin_experiment)
txt_stim = None

# Start the experimental flow
overall_samples = 0
while overall_samples < max_samples_overall:
    # Starting a new trial
    display_message(mywin, ser, data_file, timer, 'A new trial has started',
                    120, trig=trig_msg_new_trial)

    # Display fixation stim
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    mywin.callOnFlip(ser.write, trig_sample_onset)
    mywin.flip()
    log_data(data_file, onset=timer.getTime(),
             event_value=trig_sample_onset)

    trial_samples = 0
    trigger_final_choice = False
    while True:

        # A Trial starts by waiting for an action from the participant
        action, rt = inquire_action(mywin, ser, data_file, timer,
                                    timeout=float('Inf'), final=False,
                                    trig_left=trig_left_choice,
                                    trig_right=trig_right_choice,
                                    trig_final=trig_final_choice)

        # If sampling action (0 or 1), display the outcome and go on
        if action in [0, 1]:
            outcome = display_outcome(mywin, ser, data_file, timer, action,
                                      payoff_dict_1, 60, 120,
                                      trig_mask=trig_mask_outcome,
                                      trig_show=trig_outcome)

            # Increment sample counter for this trial
            trial_samples += 1

        # If sampling action 2, or the maximum of sample within a trial has
        # been reached, a final choice should be triggered
        # Afterwards, this trial has ended
        if action == 2 or trigger_final_choice:
            # Intercept if final_choice without having sampled before
            if trial_samples == 0:
                [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                display_message(mywin, ser, data_file, timer,
                                'Take at least one sample before '
                                'your final choice.', 120,
                                trig=trig_msg_zero_samples)
                [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                mywin.flip()
                continue

            # Ask participant to make a final choice
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            display_message(mywin, ser, data_file, timer,
                            'Please make your final choice.', 120,
                            trig=trig_msg_final_choice)
            [stim.setAutoDraw(True) for stim in fixation_stim_parts]
            mywin.callOnFlip(ser.write, trig_choice_onset)
            mywin.flip()
            log_data(data_file, onset=timer.getTime(),
                     event_value=trig_choice_onset)

            # Wait for the action
            action, rt = inquire_action(mywin, ser, data_file, timer,
                                        timeout=float('Inf'), final=True,
                                        keylist=['left', 'right'],
                                        trig_left=trig_left_final_choice,
                                        trig_right=trig_right_final_choice)

            # Display the outcome
            outcome = display_outcome(mywin, ser, data_file, timer, action,
                                      payoff_dict_1, 60, 120,
                                      trig_mask=trig_mask_final_outcome,
                                      trig_show=trig_final_outcome)
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            overall_samples += trial_samples

            # Start a new trial
            break

        # Check if enough samles have been taken to trigger a final choice
        # after the next sample
        if trial_samples + 1 == max_samples_per_trial:
            trigger_final_choice = True

        # Finally, get ready for the next sample within this trial
        mywin.callOnFlip(ser.write, trig_sample_onset)
        mywin.flip()
        log_data(data_file, onset=timer.getTime(),
                 event_value=trig_sample_onset)


# We are done!
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
display_message(mywin, ser, data_file, timer,
                'This task is over. Press any key to quit.',
                1, trig=trig_end_experiment)
event.waitKeys()

# Close the Window and quit
mywin.close()
core.quit()
