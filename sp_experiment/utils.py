"""Provide utility functions for the main experiment.

Only functions that do not need a direct psychopy import.

main file: sp.py

other utilities: psychopy_utils.py

"""
import numpy as np

import sp_experiment
from sp_experiment.define_payoff_settings import get_random_payoff_dict

# Frames per second. Change depending on your hardware.
utils_fps = 60


class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


def get_final_choice_outcomes(df):
    """Get a vector of the final choice outcomes.

    Parameters
    ----------
    df : pandas.DataFrame
        Data that was collected

    Returns
    -------
    outcomes : ndarray
        vector of outcomes final choices.

    """
    ntrials = int(df['trial'].max()+1)
    outcomes = np.zeros(ntrials) * np.nan
    for trial in range(ntrials):
        tmp_df = df[df['trial'] == trial]
        # The last outcome recorded in a trial is final choice outcome
        outcomes[trial] = tmp_df['outcome'].dropna().tolist()[-1]

    return outcomes


def get_payoff_dict(df, trial):
    """Get the payoff dict at a trial within the data.

    Parameters
    ----------
    df : pandas.DataFrame
        Data from where to get the payoff dict

    trial : int
        Index into the data for which to fetch the payoff dict

    Returns
    -------
    payoff_dict : dict
        Dictionary containing the reward distribution setting of the current
        trial. NOTE: returns the "final" payoff_dict that was used for
        drawing the reward

    """
    # get the setting and reformat it to fit with internal usage in
    # `define_payoff_settings.py`
    # NOTE: always take the last available setting, because the previous ones
    #       (if there are any) have been dropped due to an error (if there was
    #       one)
    tmp_df = df[(df['trial'] == trial)]
    tmp_df = tmp_df.loc[:,  'mag0_1':'prob1_2'].dropna()
    wrong_format_setting = tmp_df.iloc[-1].tolist()
    setting = np.array(wrong_format_setting)[[0, 2, 1, 3, 4, 6, 5, 7]]
    setting = np.expand_dims(setting, 0)
    # quick sanity check that we have proper roundings, for example 0.3 instead
    # of 0.29999999 ... 1., 2., 3., etc. would be fine (as magnitudes)
    for entry in setting[0]:
        assert len(str(entry)) in [2, 3]  # 2 for magnitudes, 3 for probs
    payoff_dict, payoff_settings = get_random_payoff_dict(setting)
    return payoff_dict


def get_passive_action(df, trial, sample):
    """Get data for a replay.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to be replayed

    trial, sample : int
        Indices into the data for which to fetch actions

    Returns
    -------
    keys_rts : list of tuples
        each entry in the list contains a tuple of the pressed key and the
        reaction time associated with the keypress.

    """
    admissible_actions = ['sample', 'stop', 'forced_stop', 'premature_stop']
    df = df[(df['trial'] == trial) &
            (df['action_type'].isin(admissible_actions))]
    key = int(df['action'].tolist()[int(sample)])
    rt = float(df['response_time'].tolist()[int(sample)])
    key = {0: 'left', 1: 'right', 2: 'down'}[key]
    keys_rts = [(key, rt)]
    return keys_rts


def get_passive_outcome(df, trial, sample):
    """Get data for a replay.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to be replayed

    trial, sample : int
        Indices into the data for which to fetch actions

    Returns
    -------
    outcome : int
        magnitude of the outcome to be obtained in the passive condition

    """
    df = df[(df['trial'] == trial)]
    outcomes = df[(df['trial'] == trial)]['outcome'].dropna()
    outcome = int(outcomes.tolist()[sample])
    return outcome


def get_jittered_waitframes(min_wait, max_wait, fps=utils_fps):
    """From a uniform distribution, determine a waiting time within an interval.

    Parameters
    ----------
    min_wait, max_wait :  int
        The minimum and maximum wait time in milliseconds.

    fps : int
        Refreshrate of the screen.

    Returns
    -------
    wait_frames : int
        A wait time in frames in the interval [min_wait, max_wait]

    """
    low = int(np.floor(min_wait/1000 * fps))
    high = int(np.ceil(max_wait/1000 * fps))
    wait_frames = np.random.randint(low, high+1)
    return wait_frames


def log_data(fpath, onset='n/a', duration=0, trial='n/a', action='n/a',
             outcome='n/a', response_time='n/a', value='n/a',
             payoff_dict='n/a', fps=utils_fps,
             version=sp_experiment.__version__, reset=False):
    """Write data to the log file.

    All inputs except the file path default to 'n/a'.

    See also the 'task-sp_events.json' file.

    Parameters
    ----------
    fpath : str
        Path to the log file.

    onset : float | 'n/a'
        onset of the event in seconds

    duration : int | 0
        duration of the event in frames. Will then be converted to seconds by
        dividing with `utils_fps`.

    trial : int | 'n/a'
        the number of the trial in which this event happened.

    action : int, one of [1, 2, 3] | 'n/a'
        the concrete action that the subject performed for the action type

    outcome : int | 'n/a'
        the outcome that the subject received for their action

    response_time : float | 'n/a'
        the time it took the subject to respond after the onset of the event

    value : byte | 'n/a'
        the TTL trigger value (=EEG marker value) associated with an event

    payoff_dict : dict | 'n/a'
        Dictionary containing the reward distribution setting of the current
        trial.

    fps : int
        frames per second used in this experiment

    version : str
        version of the experiment used for collecting this data

    reset : bool
        if True, discard all prior events in the current trial because of
        an error of the participant. If False, ignore it

    """
    # Infer action type
    action_type_dict = dict()
    action_type_dict[0] = 'sample'
    action_type_dict[1] = 'sample'
    action_type_dict[2] = 'stop'
    action_type_dict[3] = 'final_choice'
    action_type_dict[4] = 'final_choice'
    action_type_dict[5] = 'forced_stop'
    action_type_dict[6] = 'forced_stop'
    action_type_dict[7] = 'premature_stop'
    action_type_dict['n/a'] = 'n/a'

    action_type = action_type_dict[action]
    if action in [5, 6]:
        action = action - 5
    elif action == 7:
        action = 2
    elif action != 'n/a':
        action = (action - 3) if action in [3, 4] else action

    # Reformat reward distribution settings
    if payoff_dict != 'n/a':
        assert len(payoff_dict) == 2
        setting = list()
        for i in range(2):
            for out_i in list(set(payoff_dict[i])):
                prob_i = payoff_dict[i].count(out_i) / len(payoff_dict[i])
                setting.append(out_i)
                setting.append(prob_i)
    else:
        setting = ['n/a'] * 8
    (mag0_1, prob0_1, mag0_2, prob0_2, mag1_1, prob1_1, mag1_2,
     prob1_2) = setting

    # turn byte into integer if we sent a trigger
    value = ord(value) if isinstance(value, bytes) else 'n/a'

    # Write the data
    with open(fpath, 'a') as fout:
        data = [onset,
                duration / fps,
                trial,
                action_type, action, outcome, response_time,
                value,
                mag0_1, prob0_1, mag0_2, prob0_2,
                mag1_1, prob1_1, mag1_2, prob1_2,
                version,
                int(reset)]
        line = '\t'.join([str(i) for i in data])
        fout.write(line + '\n')


def set_fixstim_color(stim, color):
    """Set the fill and line color of a stim."""
    stim.setFillColor(color)
    stim.setLineColor(color)
    return stim
