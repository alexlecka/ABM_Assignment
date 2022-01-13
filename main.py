from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
import matplotlib.pyplot as plt
from mesa import Agent, Model
import random

# load all available schedulers
import mesa.time as time

from RecyclingCompany import RecyclingCompany

from Municipality import initialize_one_municipality

#%%

debugging = False
alex_debug = False
rapha_debug = True

def rapha_print(string = ''):
    if rapha_debug:
        print(string)

def alex_print(string = ''):
    if alex_debug:
        print(string)

def debug_print(string = ''):
    if debugging:
        print(string)

#%% model

# the following list represent
# [number_id, home_collection, 
# population_distribution, 
# budget_plastic_recycling, 
# recycling_target, 
# priority_price_over_recycling]

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

# this is only for testing! with one municipality
# defined_municipalities = [[1, True, [1, 1], 1000, 0.65, 1]]

class ABM_model(Model):

    def __init__(self, defined_municipalities, n_recycling_companies):
        
        debug_print('***** AGENT-BASED MODEL *****')
        debug_print('Initializing the model and the agents.')
        debug_print()
        
        # initialization 
        self.number_municipalities = len(defined_municipalities)
        
        self.schedule_municipalities = RandomActivation(self)
        self.schedule_households = RandomActivation(self)
        self.schedule_recycling_companies = RandomActivation(self)

        # Recycling performance indicatiors
        ## Initialized with 1 to avoid devision by zero. All values get set to 0 at beginning of step function
        self.total_potential_plastic_waste = 1 #total mass of plastic waste present in base waste (not what ends up in plastic waste)
        self.total_plastic_waste = 1 #total mass of plastic waste that ended up in plastic waste fit for recycling
        self.total_recycled_plastic = 1 #total mass of plastic that recycling companies recycled
        
        self.municipalities = []
        self.households = []
        self.recycling_companies = []
        
        self.offer_requests = []
        
        self.tick = 0


        ### Debug variables ###
        self.debug_count_fee = 0

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
            self.schedule_households.add(self.households[i])

        # initialization of recycling companies and adding them to scheduler
        for i in range(n_recycling_companies):
            recycling_company = RecyclingCompany('R_{}'.format(i), self)
            self.recycling_companies.append(recycling_company)
            self.schedule_recycling_companies.add(recycling_company)
            
        if self.number_municipalities == 1:
            debug_print('There is 1 municipality with:')
        else:
            debug_print('There are {} municipalities with:'.format(self.number_municipalities))
        for municipality in self.municipalities:
            debug_print('Municipality {} with population distribution {}, budget {} and a recycling rate target {}.'.format(
                        municipality.id, municipality.population_distribution, municipality.budget_plastic_recycling,
                        municipality.recycling_target))
        debug_print()

    def step(self):
        # Reset counters
        self.total_potential_plastic_waste = 0
        self.total_plastic_waste = 0
        self.total_recycled_plastic = 0

        # iterate in random order over municipalities to establish order
        municipalities_index_list = list(range(len(self.municipalities)))
        random.shuffle(municipalities_index_list)
        
        # municipalities receive funding if it is the start of the year
        if self.tick%12 == 0:
            for municipality in self.municipalities:
                debug_print('Start of the year - municipality {} receives government funding.'.format(municipality.id))
                municipality.receive_funding()
                debug_print('New budget is {}.'.format(municipality.budget_plastic_recycling))

        # Households in municipalities produce waste
        for municipality in self.municipalities:
            for household in municipality.households:
                household.calc_base_waste(self.tick)
                household.calc_plastic_waste(self.tick)

                # Add potential_plastic waste to total_potential_plastic waste
                self.total_potential_plastic_waste += household.potential_plastic_waste
                self.total_plastic_waste += household.plastic_waste

        # Contract closing
        ## municipalities in need of a new recycling company announce it to the market by requesting an offer
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

        # reset offers
        self.offer_requests = []
                
        # recycling company treats waste (recycling = selling and burning)
        # this means that a portion of the plastic waste gets recycled - first determine this amount
        for municipality in self.municipalities:
            municipality.plastic_waste = 0
            for household in municipality.households:
                municipality.plastic_waste += household.plastic_waste
            # Mass of plastic whichis recycled by the recycling company is calculated here
            municipality.recyclable = municipality.plastic_waste * municipality.contract['recycling_rate']

            # Add mass mass of recycled plastic to total_recycled_plastic
            self.total_recycled_plastic += municipality.recyclable




        
            debug_print()
            debug_print('Municipality {} produces waste out of which {} is plastic waste:'.format(municipality.id, municipality.plastic_waste))
            data = municipality.format_table_waste()
            alex_print(data)
        
        # check contract conditions - has municipality delivered enough plastic waste, etc.?
        for municipality in self.municipalities:
            
            debug_print()
            debug_print('Municipality {} produces {} of recyclable plastic waste.'.format(municipality.id,
                                                                                          municipality.recyclable))
            
            debug_print('Recycling company {} budget {}.'.format(municipality.contract['recycling_company'].id,
                                                                 municipality.contract['recycling_company'].budget))
            
            debug_print()
            debug_print('Municipality pays for waste processing and recycling company receives money.')
            
            # 1: municipality pays for waste processing
            municipality.budget_plastic_recycling -= municipality.contract['price'] * municipality.plastic_waste

            # 2: recycling company gets paid for waste processing
            municipality.contract['recycling_company'].budget += municipality.contract['price'] * municipality.plastic_waste
            debug_print(municipality.contract['recycling_company'].budget)
            municipality.contract['recycling_company'].budget -= municipality.contract['recycling_company'].opex
            debug_print(municipality.contract['recycling_company'].opex)
            debug_print(municipality.contract['recycling_company'].budget)
            debug_print('Recycling company {} budget {}.'.format(municipality.contract['recycling_company'].id,
                                                                 municipality.contract['recycling_company'].budget))
            debug_print('Municipality {} budget_plastic_recycling {}.'.format(municipality.id,
                                                                              municipality.budget_plastic_recycling))

            # 3: recycling company gets paid fee, in case the municipality did not deliver enoug waste
            if municipality.plastic_waste < municipality.contract['minimal_plastic_waste_mass']:
                debug_print('Municipality failed to deliver enough waste so has to pay a fee.')
                
                # 3.1 the mass off the missing waste is calculated
                missing_waste = municipality.contract['minimal_plastic_waste_mass'] - municipality.plastic_waste

                # 3.2: municipality pays fee
                municipality.budget_plastic_recycling -= municipality.contract['fee'] * missing_waste

                # 3.3: recycling company gets paid the fee
                municipality.contract['recycling_company'].budget += municipality.contract['fee'] * missing_waste
                debug_print(
                    'Municipality {} pays a fee of {} and the recycling company received money.'.format(municipality.id, municipality.contract['fee'] * missing_waste))

                self.debug_count_fee += 1

            # 4: recycling company gets paid for sold recycled waste
            debug_print('Recycling company sells the recycled waste and receives money.')
            
            municipality.contract['recycling_company'].budget += (municipality.recyclable)*1.5 # 1.5 is the price per kg a company can sell

            debug_print('Recycling company {} budget {}.'.format(municipality.contract['recycling_company'].id,
                                                                 municipality.contract['recycling_company'].budget))

        # perform outreach based on how much budget the municipality has available
        for municipality in self.municipalities:
            if municipality.budget_plastic_recycling >= 500 and municipality.outreach['learn'] == 0 and municipality.outreach['forget'] == 0:
                debug_print()
                debug_print('Municipality {} has money for outreach so the recycling perception and knowledge will go up.'.format(
                             municipality.id))
                data = municipality.format_table_outreach()
                alex_print(data)
                
                municipality.outreach['learn'] = 1
                municipality.outreach['stay'] = 0
            else:
                debug_print()
                debug_print('Municipality {} will not educate its citizenz on recycling.'.format(
                             municipality.id))
            municipality.do_outreach()
            
            data = municipality.format_table_outreach()
            alex_print(data)

        self.tick += 1

#%% testing the model

random.seed(4)

model = ABM_model(defined_municipalities, 10)

#%%

example_i = 0

for i in range(50):
    rapha_print('Tick {}'.format(i))
    debug_print('_____________________________________________________________')
    debug_print()
    debug_print('Tick {}: municipality {} budget_plastic_recycling {}.'.format(i, model.municipalities[example_i].id, 
                                                                 model.municipalities[example_i].budget_plastic_recycling))
    debug_print('Recycling rate of total potential recyclable plastic: {}'.format(model.total_recycled_plastic / model.total_potential_plastic_waste))
    model.step()

debug_print('{} times a fee was payed'.format(model.debug_count_fee))
#%%


#%% print out stuff of individuals

# print()
# if len(model.municipalities) == 1:
#     print('There is 1 municipality.')
# else:
#     print('There are {} municipalities.'.format(len(model.municipalities)))
# print('Example: Municipality {} has a population distribution of {} and {} total households.'.format(model.municipalities[example_i].id,
#                                                                                                      model.municipalities[example_i].population_distribution,
#                                                                                                      len(model.municipalities[example_i].households)))
# print('Household IDs: ',[one_household.id for one_household in model.municipalities[example_i].households])

# print()
# print('The municipality has a contract with the recycling company {}.'.format(model.municipalities[example_i].contract['recycling_company']))
# print()
# print('Contract:')
# print(model.municipalities[example_i].contract)

# print()
# print('check: ', model.municipalities[example_i].budget_plastic_recycling)

#%%

# The dictionary which is now the contract is refered to by the company and the municipality
# If an entry changes for the municipality, it also changes for the company.
# print(model.municipalities[0].contract)
# print(model.municipalities[0].id)
#
# print(model.municipalities[0].contract['recycling_company'].contract['M_1'])
#
# model.municipalities[0].contract['active'] = 'bananarama'
#
# print(model.municipalities[0].contract['recycling_company'].contract['M_1'])
# print(model.municipalities[0].contract)


