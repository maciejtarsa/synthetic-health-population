#!/usr/bin/python3
import random

# a helper function for setting initial probabilities for each module
def set_initial_prob(module, data, patient):
    """
    Set initial probabilities for each module
    Including recalculating them based on static characteristics
    Parameters:
        module: module name
        data: a dataframe of input settings
        patient: a dictionary of patient object
    Returns:
        states: a list of possible states
        t_probabilities: transition probabilities
        m_probabilities: multiplication values for probabilities
    """
    # set states
    states = data.iloc[:,3:-1].columns.tolist()
    # extract the initial transitions
    initial_tran = data.loc[data['type'] == 'initial_tran']
    # and multiplications
    transition = data.loc[data['type'] == 'transition']
    # and static characteristics
    characteristics_static = data.loc[data['type'] == 'characteristics_static']
    # set transition probabilities and multiply values
    t_probabilities = []
    m_probabilities = []
    # iterate over a number of states
    for i in range(len(states)):
      t_probabilities.append(initial_tran.iloc[i,3:-1].values.tolist())
      m_probabilities.append(transition.iloc[i,3:-1].values.tolist())

    ## amend initial transitions based on static characteristics
    for index, row in characteristics_static.iterrows():
      multiplications = amend_prob_char(row, patient)
      t_probabilities = amend_prob(t_probabilities, [multiplications,multiplications,multiplications])

    return states, t_probabilities, m_probabilities

# a helper function for selecting next state from a list of states with probabilities
def mcmc(states, probabilities, initial_state):
  """
  Returns the next state given an initial state
  Parameters:
    states: a list of possble states
    probabilities: a matrix of probabilities of each state turning into another
    initial_state: a string containing one of the possible states
  Returns:
    next_state: next_state calculated based on probabilities
  """
  # first, generate a list of possible transitions
  transitions = []
  # iterate through the transitions twice
  for state1 in states:
    state_transitions = []
    for state2 in states:
      state_transitions.append((state1, state2)) 
      transitions.append(state_transitions)
  # set up an empty return value
  next_state = ''
  # based on given probabilities, choose the next state
  for i in range(len(states)):
      if initial_state == states[i]:
        change = random.choices(transitions[i], probabilities[i], k=1)[0]
        for j in range(len(states)):
          if change == transitions[i][j]:
            next_state = states[i]
          if change == transitions[i][j]:
            next_state = states[j]
          if change == transitions[i][j]:
            next_state = states[j]
  return next_state

# a fuction to amend probabilities based on multiplication values
def amend_prob(probabilities, amendments):
  """
  Amend probabilities based on provided values
  Parameters:
    probabilities: a list of list of probabilities for transitions
    amendments: a list of lists of values to multiply the probabilities by
  Returns:
    normalised list of lists of probabilities
  """
  for i in range(len(probabilities)):
    probabilities[i] = [a*b for a,b in zip(probabilities[i], amendments[i])]
    probabilities[i] = [float(j)/sum(probabilities[i]) for j in probabilities[i]]
  return probabilities

# a function to multiply probabilities based on characteristics
def amend_prob_char(characteristic, current_data, previous_data = {}):
  """
  A function to iterate over given characteristics and extract relevant
  multiplications.
  Parameters:
    characteristics: a row of a dataframe containing characteristics
    current_data: a dictionary containing patient or timeline information
    previous_data: a dictionary containing previous timeline, by default an empty dict
  Returns:
    mulitplications: either list of 1s or multiplication to multiply probabilities by
  """
  # get the number of possible states
  no_states = len(characteristic[3:-1])

  # by default, set multiplicaton to to a list of 1s
  multiplications = [1 for i in range(no_states)]

  if characteristic['variable'] in current_data.keys():
    # check if it refers to greater than
    if characteristic['value'][0] == '>':
      if int(current_data[characteristic['variable']]) > int(characteristic['value'][1:]):
        # get multiplication values
        multiplications = characteristic[3:-1].values
    # or less than
    elif characteristic['value'][0] == '<':
      if int(current_data[characteristic['variable']]) < int(characteristic['value'][1:]):
        multiplications = characteristic[3:-1].values
    # otherwise assume equals
    else:
      if current_data[characteristic['variable']] == characteristic['value']:
        multiplications = characteristic[3:-1].values
  # check if that characteristic is present in previous timeline
  # this allows for circular dependencies to take effect
  elif (previous_data != None) & (characteristic['variable'] in previous_data.keys()):
    # check if it refers to greater than
    if characteristic['value'][0] == '>':
      if int(previous_data[characteristic['variable']]) > int(characteristic['value'][1:]):
        # get multiplication values
        multiplications = characteristic[3:-1].values
    # or less than
    elif characteristic['value'][0] == '<':
      if int(previous_data[characteristic['variable']]) < int(characteristic['value'][1:]):
        multiplications = characteristic[3:-1].values
    # otherwise assume equals
    else:
      if previous_data[characteristic['variable']] == characteristic['value']:
        multiplications = characteristic[3:-1].values

  return multiplications

# module runner
def run_module(module, data, age_range, patient, current_timeline, previous_timeline, module_dict):
  """
  A function to generate a record for current age range.
  Parameters:
    module: module name
    data: input data for that module
    age_range: current age range
    patient: a dictionary of patient information
    current_timeline: a dictionary of current timeline so far
    previous_timeline: a dictionary of previours timeline
    module_dict: a dictionary of states and probabilities for modules
  Returns:
    state: selected state
    module_dict: an update dictionary of modules
  """
  # get the patients id
  id = patient['id']

  # extract states, t and m probabilities from the module dict
  states = module_dict[module][0]
  t_probabilities = module_dict[module][1]
  m_probabilities = module_dict[module][2]

  # extract the demographic details
  initial = data.loc[data['type'] == 'initial']
  characteristics_static = data.loc[data['type'] == 'characteristics_static']
  characteristics_dynamic = data.loc[data['type'] == 'characteristics_dynamic']

  # if age range is included in the initial set up
  if age_range in initial['value'].values:
    ## initial set up
    # iterate over each variable and amend as relevant
    for index, row in initial.iterrows():
      if age_range == row['value']:
        probabilities = row[3:-1].values
      
    ## amend initial setup based on static characteristics
    for index, row in characteristics_static.iterrows():
      multiplications = amend_prob_char(row, patient)
      probabilities = amend_prob([probabilities], [multiplications])[0]

    # set the state status
    state_status = random.choices(states, probabilities, k=1)[0]

  ## transitions
  # if age_range is not included in the set up
  if age_range not in initial['value'].values:
    # amend transitions based on dynamic characteristics
    for index, row in characteristics_dynamic.iterrows():
      multiplications = amend_prob_char(row, current_timeline, previous_timeline)
      t_probabilities = amend_prob(t_probabilities, [multiplications,multiplications,multiplications])

    # choose the next state
    state_status = mcmc(states, t_probabilities, module_dict[module][3])
    # amend the probabilities based on multiplications
    # ready for the next age range
    t_probabilities = amend_prob(t_probabilities, m_probabilities)

  # update the module dictionary with new t probabilities
  module_dict[module] = (states, t_probabilities, m_probabilities, state_status)

  # return the status for that timeline and module and the update module_dict
  return state_status, module_dict