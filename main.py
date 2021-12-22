from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import matplotlib.pyplot as plt
from mesa import Agent, Model
import numpy as np
import random

#load all available schedulers
import mesa.time as time

from RecyclingCompany import RecyclingCompany
from Municipality import Municipality
from Household import Household

from Municipality import initialize_one_municipality

#%%

debugging = True

def debug_print(string):
    if debugging:
        print(string)

#%% model

# the following list represent
# [number_id, home_collection, 
# population_distribution, 
# budget_plastic_recycling, 
# recycling_target, 
# priority_price_over_recycling] of 10 municipalities

defined_municipalities = [[1, True, [54, 54, 54, 18], 96,  0.5, 1],
                          [2, False, [32, 24, 16, 8], 123, 0.6, 0.1],
                          [3, False, [7, 14, 28, 21], 126, 0.6, 0.2],
                          [4, True, [60, 30, 52, 8], 107, 0.7, 0.5],
                          [5, True, [0, 1, 6, 2], 136, 0.6, 0.2],
                          [6, False, [64, 32, 56, 8], 109, 0.4, 0.7],
                          [7, False, [39, 39, 39, 13], 96, 0.7, 0.3],
                          [8, True, [14, 21, 28, 7], 70, 0.5, 0.6],
                          [9, False, [36, 27, 18, 9], 106, 0.5, 0.5],
                          [10, True, [21, 21, 14, 14], 120, 0.6, 0.4]]

class ABM_model(Model):

    def __init__(self, defined_municipalities, n_recycling_companies):
        
        # initialization 
        self.number_municipalities = len(defined_municipalities)
        
        self.schedule_municipalities = RandomActivation(self)
        self.schedule_households = RandomActivation(self)
        self.schedule_recycling_companies = RandomActivation(self)
        
        
        self.municipalities = []
        self.households = []
        self.recycling_companies = []
        
        self.offer_requests = []
        self.tick = 0

        for defined_municipality in defined_municipalities:
            self.municipalities.append(initialize_one_municipality(defined_municipality[0],
                                                                   defined_municipality[1],
                                                                   defined_municipality[2],
                                                                   defined_municipality[3],
                                                                   defined_municipality[4],
                                                                   defined_municipality[5], self))

        # adding municipalities to scheduler, populating households list
        for i in range(self.number_municipalities):
            self.schedule_municipalities.add(self.municipalities[i])
            self.households = self.households + self.municipalities[i].households

        # adding municipalities to household scheduler
        for i in range(len(self.households)):
            # print(household)
            self.schedule_households.add(self.households[i])

        # initialization of recycling companies and adding them to scheduler
        for i in range(n_recycling_companies):
            temp_recycling_company = RecyclingCompany('R_{}'.format(i), self)
            self.recycling_companies.append(temp_recycling_company)
            self.schedule_recycling_companies.add(temp_recycling_company)

    def step(self):
        print('Tick {}'.format(self.tick))

        # iterate in random order over municipalities
        municipalities_index_list = list(range(len(self.municipalities)))
        random.shuffle(municipalities_index_list)

        # companies in need for a new Recycling Companies announce it to the market
        for municipality_index in municipalities_index_list:
            offer = self.municipalities[municipality_index].request_offer(self.tick)

            if offer != None:
                self.offer_requests.append(offer)

        # recycling companies send offers ro municipalities
        for recycling_company in self.recycling_companies:
            recycling_company.provide_offer(self.offer_requests)


        for municipality in self.offer_requests:
            municipality.select_offer(self.tick)

        self.offer_requests = []

        self.tick += 1


#%% testing the model

test_model = ABM_model(defined_municipalities, 10)
for i in range(40):
    test_model.step()

#%% print out stuff of individuals

print(len(test_model.municipalities[2].households))
print(test_model.municipalities[2].number_households)
print(test_model.municipalities[1].contract[1].contract)

#%%
print(test_model.municipalities[0].contract)
