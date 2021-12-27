from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import matplotlib.pyplot as plt
from mesa import Agent, Model
import random

# load all available schedulers
import mesa.time as time

from RecyclingCompany import RecyclingCompany

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

defined_municipalities = [[1, True, [54, 54], 96,  0.5, 1],
                          [2, False, [32, 24], 123, 0.6, 0.1],
                          [3, False, [7, 14], 126, 0.6, 0.2],
                          [4, True, [60, 30], 107, 0.7, 0.5],
                          [5, True, [10, 1], 136, 0.6, 0.2],
                          [6, False, [64, 32], 109, 0.4, 0.7],
                          [7, False, [39, 39], 96, 0.7, 0.3],
                          [8, True, [14, 21], 70, 0.5, 0.6],
                          [9, False, [36, 27], 106, 0.5, 0.5],
                          [10, True, [21, 21], 120, 0.6, 0.4]]

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
            recycling_company = RecyclingCompany('R_{}'.format(i), self)
            self.recycling_companies.append(recycling_company)
            self.schedule_recycling_companies.add(recycling_company)

    def step(self):
        # print('Tick {}'.format(self.tick))

        # iterate in random order over municipalities to establish order
        municipalities_index_list = list(range(len(self.municipalities)))
        random.shuffle(municipalities_index_list)

        # municipalities in need of a new recycling company announce it to the market by requesting an offer
        for municipality_index in municipalities_index_list:
            offer = self.municipalities[municipality_index].request_offer(self.tick)

            if offer != None:
                self.offer_requests.append(offer)

        # recycling companies send offers to municipalities
        for recycling_company in self.recycling_companies:
            recycling_company.provide_offer(self.offer_requests)

        # municipalities select an offer based on their behavior (select cheapest one for a given recycling rate)
        for municipality in self.offer_requests:
            municipality.select_offer(self.tick)

        self.offer_requests = []
        
        # households produce (plastic) waste
        for municipality in self.municipalities:
            for household in municipality.households:
                household.calc_base_waste(self.tick)
                household.calc_plastic_waste(self.tick)
                
        # recycling company treats waste (recycling = selling and burning)
        # this means that a portion of the plastic waste gets recycled - first determine this amount
        recyclable = 0
        for municipality in self.municipalities:
            for household in municipality.households:
                recyclable += household.plastic_waste*municipality.contract[2]
            municipality.recyclable = recyclable
            recyclable = 0
        
        # check contract conditions - has municipality delivered enough plastic waste, etc.?
        # at the moment, we do not have the minimum amount to be delivered defined, so always good
        for municipality in self.municipalities:
            if municipality.recyclable > 0:
                # is ok 
                # 1: municipality pays for waste processing 
                municipality.budget_plastic_recycling -= municipality.contract[3]       
                
                # 2: recycling company gets paid for waste processing
                municipality.contract[1].budget += municipality.contract[3]
                
                # 3: recycling company gets paid for sold recycled waste
                municipality.contract[1].budget += (municipality.recyclable/1000)*1.5
            else:             
                # not ok, municipality pays for waste processing and a fine
                # 1: municipality pays for waste processing 
                municipality.budget_plastic_recycling -= municipality.contract[3]       
                
                # 2: recycling company gets paid for waste processing
                municipality.contract[1].budget += municipality.contract[3]
                
                # 3: municipality pays fee
                municipality.budget_plastic_recycling -= municipality.contract[4] 
                
                # 4: recycling company gets paid the fee
                municipality.contract[1].budget += municipality.contract[4] 

        self.tick += 1

#%% testing the model

random.seed(4)

model = ABM_model(defined_municipalities, 10)

for i in range(40):
    model.step()

#%% print out stuff of individuals

print()
print('There are {} municipalities.'.format(len(model.municipalities)))
example_i = 4
print('Example: Municipality {} has a population distribution of {} and {} total households.'.format(model.municipalities[example_i].unique_id,
                                                                                                     model.municipalities[example_i].population_distribution,
                                                                                                     len(model.municipalities[example_i].households)))
print('Household IDs: ',[one_household.unique_id for one_household in model.municipalities[example_i].households])

print()
print('The municipality has {} types of households.'.format(model.municipalities[example_i].number_households))

print()
print('The municipality has a contract with the recycling company {}.'.format(model.municipalities[example_i].contract[1]))
print(model.municipalities[example_i].contract)

print()
print('check: ', model.municipalities[example_i].budget_plastic_recycling)
