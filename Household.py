from mesa import Agent
import numpy as np

#%% variables affecting households

share_plastic_in_total_waste = 0.2

class Household(Agent):
    def __init__(self, unique_id, model, household_type, perception, knowledge):
        
        super().__init__(unique_id, model)
        self.id = unique_id
        
        # perception is separation, knowledge is how well we separate
        self.type = household_type
        self.perception = perception
        self.knowledge = knowledge
        self.potential_plastic_waste = 0 # total plastic waste in mass present in the base waste
        self.plastic_waste = 0 # mass of plastic waste which ends up in the plastic bin fit for recycling

    def starting_val(self, h_type):
        base = 40 
        if h_type == 'one_person':
            return 1*base
        elif h_type == 'multi_person':
            multiplier = 2.85
            return multiplier*base
        else:
            print('Do not know this household type.')
            
    def calc_starting_val(self):
        starting_value = self.starting_val(self.type)
        self.starting_value = starting_value
        self.base_waste = starting_value # needs to be copied in since a base waste is needed in the very beginning to close contracts
        
    def base_waste_eq(self, start, t):
        return start - 0.04*t - np.exp(-0.01*t)*np.sin(0.3*t)
            
    def calc_base_waste(self, t):
        waste = self.base_waste_eq(self.starting_value, t)
        self.base_waste = waste
    
    def calc_plastic_waste(self, t):
        # perception as we use it here is equal to plastic fraction
        self.plastic_waste = self.base_waste * share_plastic_in_total_waste * self.perception * self.knowledge
        self.potential_plastic_waste = self.base_waste * share_plastic_in_total_waste

    # overriding of __str__ to get some useful information when calling print on household
    def __str__(self):
        return 'Household ID: {}'.format(self.id)