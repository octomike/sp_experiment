"""Definitions for the TTL triggers to be sent.

main file: sp.py

For more information, see also the "event_value" key within the
define_variable_meanings.make_events_json_dict.

"""


def provide_trigger_dict():
    """Provide a dictionnary mapping str names to byte values."""
    trigger_dict = dict()

    # At the beginning and end of the experiment ... take these triggers to
    # crop the meaningful EEG data. Make sure to include some time BEFORE and
    # AFTER the triggers so that filtering does not introduce artifacts into
    # important parts.
    trigger_dict['trig_begin_experiment'] = bytes([1])
    trigger_dict['trig_end_experiment'] = bytes([2])

    # Indication when a new trial is started
    trigger_dict['trig_new_trl'] = bytes([3])

    # Wenever a new sample within a trial is started (fixation stim)
    trigger_dict['trig_sample_onset'] = bytes([4])

    # Whenever a choice is being inquired during sampling
    trigger_dict['trig_left_choice'] = bytes([5])
    trigger_dict['trig_right_choice'] = bytes([6])
    trigger_dict['trig_final_choice'] = bytes([7])

    # When displaying outcomes during sampling
    trigger_dict['trig_mask_outcome'] = bytes([8])
    trigger_dict['trig_show_outcome'] = bytes([9])

    # Indication when a final choice is started
    trigger_dict['trig_new_final_choice'] = bytes([10])

    # Whenever a final choice is started (fixation stim)
    trigger_dict['trig_final_choice_onset'] = bytes([11])

    # Inquiring actions during CHOICE
    trigger_dict['trig_left_final_choice'] = bytes([12])
    trigger_dict['trig_right_final_choice'] = bytes([13])

    # Displaying outcomes during CHOICE
    trigger_dict['trig_mask_final_outcome'] = bytes([14])
    trigger_dict['trig_show_final_outcome'] = bytes([15])

    # trigger for ERROR, when a trial has to be reset
    # (ignore all markers prior to this marker within this trial)
    trigger_dict['trig_error'] = bytes([16])

    # If the subject sampled a maximum of steps and now wants to take yet
    # another one, we force stop and initiate a final choice
    trigger_dict['trig_forced_stop'] = bytes([17])

    # If subject tried to make a final choice before taking at least one sample
    trigger_dict['trig_premature_stop'] = bytes([18])

    # Display the block feedback
    trigger_dict['trig_block_feedback'] = bytes([19])

    return trigger_dict
