from classes import Household
# from classes import Municipality
# from classes import RecyclingCompany

from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner
from mesa.time import RandomActivation
from mesa import Model, Agent
from mesa.space import Grid

class HouseholdRecycling(Model):
    def __init__(self, n_households = 100):
        
        # initialize households as described in Drive
        household_list = []
        for i in range(n_households):
            if i < 0.39*n_households:
                household_list.append(Household('one_person', 0.5, 0.5))
            else:
                household_list.append(Household('multi_person', 0.5, 0.5))
            household_list[-1].calc_starting_val()
            
        # initialize municipalities
        
        # initialize recycling companies 
        
    def step(self):
        # here goes the main step function of the entire model 