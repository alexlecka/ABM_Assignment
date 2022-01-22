from Household import Household
from mesa import Agent
import pandas as pd
import random

# variables
share_estimated_waste = 0.99 # for contract, estimated waste of municipality for contract

debugging = False
def debug_print(string = ''):
    if debugging:
        print(string)

class Municipality(Agent):
    def __init__(self, unique_id, model, home_collection, population_distribution, 
                 budget_plastic_recycling, recycling_target, priority_price_over_recycling):

        # attributes
        super().__init__(unique_id, model)
        self.id = unique_id
        self.home_collection = home_collection
        self.population_distribution = population_distribution # list [number of one person households, number of multi person households]
        self.estimated_plastic_waste_mass = 0  # depends on households curve needs to be checked
        self.budget_plastic_recycling = budget_plastic_recycling
        self.recycling_target = recycling_target
        self.priority_price_over_recycling = priority_price_over_recycling
        self.households = []
        self.recyclable = 0 # mass of plastic waste the recycling company can recycle. It is here for implementation reasons
        self.plastic_waste = 0 # mass either kg or tons
        self.outreach = {'policy':['reverse_waste_collection', 'education', 'container_labeling'],
                         'perception_increase':{'reverse_waste_collection':0.2,
                                                'education':0.1,
                                                'container_labeling':0},
                         'knowledge_increase':{'reverse_waste_collection':-0.1,
                                                'education':0.1,
                                                'container_labeling':0.1},
                         'cost':{'reverse_waste_collection':5000,
                                                'education':750,
                                                'container_labeling':1000},
                         'on_bool':{'reverse_waste_collection':0,
                                    'education':0,
                                    'container_labeling':0}}      
        self.contract = {'active' : False,
                         'recycling_company' : None,
                         'recycling_rate' : None,
                         'price' : None,
                         'fee' : None,
                         'expiration_tick' : None,
                         'minimal_plastic_waste_mass' : None}

        # variables for contract closing
        self.received_offers = []

        # initiate households
        count = 0
        for household_type, type_index in zip(['one_person', 'multi_person'], [0,1]):
            for i in range(self.population_distribution[type_index]): # description of population_distribution see above
                perception, knowledge = 0.5, 0.5
                self.households.append(Household('{}_H_{}'.format(self.id, count), model, household_type, perception, knowledge))
                self.households[-1].calc_starting_val()

                count += 1

    def __str__(self):
        return 'Municipality ID: {}'.format(self.id)

    def print_all_atributes(self):
        print('ID {}'.format(self.id))
        print('number_households: {}'.format(self.number_households))
        print('home_collection: {}'.format(self.home_collection))
        print('population_distribution: {}'.format(self.population_distribution))
        print('estimated_plastic_waste_mass: {}'.format(self.estimated_plastic_waste_mass))
        print('budget_plastic_recycling: {}'.format(self.recycling_target))
        print('priority_price_over_recycling: {}'.format(self.priority_price_over_recycling))
        print('contract: {}'.format(self.contract))

    def request_offer(self, tick):
        # if a contract is expired, the municipality calculates its estimated waste volume and requests offers by announcing
        # it to the environment
        
        if tick == self.contract['expiration_tick']:
            self.contract['active'] = False
            debug_print()
            debug_print('Municipality {} needs a new contract due to expiration.'.format(self.id))

            # count down the capacity tick of the company
            self.contract['recycling_company'].number_municipalities -= 1

        if self.contract['active'] == False:
            debug_print()
            debug_print('Municipality {} reports needing a new contract.'.format(self.id))

            # calculation of estimated waste volume
            # iterate over households and get current waste volume (last known to municipality)
            current_plastic_waste_mass = [household.plastic_waste for household in self.households]
            
            # 80% of the sum of this base waste is the estimated waste volume
            self.estimated_plastic_waste_mass = share_estimated_waste * sum(current_plastic_waste_mass)

            # just return the reference to the municipality
            return self 
        else:
            return None

    def select_offer(self, tick):
        # reevaluate price over recycling priority if it is not the very beginning
        if tick != 0:
            # calculate number of months left till funding comes
            months_year_left = 12 - tick % 12

            # calculate budget per month left after waste is paid
            monthly_budget = self.budget_plastic_recycling / months_year_left - self.estimated_plastic_waste_mass * self.contract['price']

            # increase or decrease priority ofer price by 0.1
            dpriority_price_over_recycling = 0.1
            if monthly_budget > 0:
                self.priority_price_over_recycling -= dpriority_price_over_recycling
                if self.priority_price_over_recycling < 0:
                    self.priority_price_over_recycling = 0
                debug_print('Municipality {} decreased priority_price_over_recycling to {}'.format(self.id, self.priority_price_over_recycling))
            else:
                self.priority_price_over_recycling += dpriority_price_over_recycling
                if self.priority_price_over_recycling > 1:
                    self.priority_price_over_recycling = 1
                debug_print('Municipality {} increased priority_price_over_recycling to {}'.format(self.id, self.priority_price_over_recycling))

        # evaluate offers (see documentation for reasoning behind formular)
        random.shuffle(self.received_offers) # shuffling, since if there are several offers scoring equally well, always the first is selected
        scoring_offers = []
        # debug_print()
        # debug_print('Offer selection of municipality {}, options:'.format(self.id))
        # debug_print(self.received_offers)

        # delete companies from list that do not have capacities anymore
        offers_to_check = self.received_offers
        self.received_offers = []
        for offer in offers_to_check:
            if offer['recycling_company'].number_municipalities < offer['recycling_company'].capacity_municipalities:
                self.received_offers.append(offer)

        # score the available offers
        for received_offer in self.received_offers:
            # calculate an offer index = evaluation 
            scoring_offers.append((self.recycling_target / received_offer['efficiency'] * received_offer ['price']) + self.priority_price_over_recycling * received_offer['price'])
            # first term gets smaller the better the efficiency and the lower the price
            # second term get smaller when priority_price_over_recycling is small -> it is a penalty term penalizing high prices
            # if the second term is small, it means that the municipality cares more about the recycling rate then the money.
        # select index of best offer
        index_best_offer = scoring_offers.index(min(scoring_offers))

        # check whether this is the very initialization
        contract_duration = 36 # months
        if tick == 0:
            # if we are at the start, give the contract varied validity so that not all municipalities :
            # run out of contracts at the same time 
            expiration_tick = random.randint(1, contract_duration)
        else:
            # otherwise contracts run for 3 years = 36 months
            expiration_tick = tick + contract_duration

        # write contract into variable
        self.contract['active'] = True
        self.contract['recycling_company'] = self.received_offers[index_best_offer]['recycling_company']
        self.contract['recycling_rate'] = self.received_offers[index_best_offer]['efficiency']
        self.contract['price'] = self.received_offers[index_best_offer]['price']
        self.contract['fee'] = 0.2 * self.received_offers[index_best_offer]['price'] # needs to be changed tk
        self.contract['expiration_tick'] = expiration_tick
        self.contract['minimal_plastic_waste_mass'] = self.estimated_plastic_waste_mass

        # add municipality to contract
        self.contract['municipality'] = self

        # give recycling company the contract
        self.received_offers[index_best_offer]['recycling_company'].contract[self.id] = self.contract

        # apply the customer counter in the recycling company
        debug_print('Counter company: {}'.format(self.contract['recycling_company'].number_municipalities))
        self.contract['recycling_company'].number_municipalities += 1
        debug_print('Counter company: {}'.format(self.contract['recycling_company'].number_municipalities))
        
        debug_print()
        debug_print('Municipality {} has chosen {} with {}.'.format(self.id, self.contract['recycling_company'].id, 
                                                                    self.contract))

        self.received_offers = []
        
    def do_outreach(self, todo):
        if todo == 'stay':
            forgetting = 0.005
            length_forgetting = 13
            if self.outreach['on_bool']['education'] == length_forgetting:
                self.outreach['on_bool']['education'] = 0
            if self.outreach['on_bool']['education'] >= 1 and self.outreach['on_bool']['education'] < length_forgetting:
                for household in self.households:
                    household.perception -= forgetting
                    household.knowledge -= forgetting
                self.outreach['on_bool']['education'] += 1
        else:
            for household in self.households:
                household.perception += self.outreach['perception_increase'][todo]
                if household.perception > 1:
                    household.perception = 1
                if household.knowledge > 1:
                    household.knowledge= 1
                household.knowledge += self.outreach['knowledge_increase'][todo]
            self.outreach['on_bool'][todo] = 1
            self.budget_plastic_recycling -= self.outreach['cost'][todo]
                    
    def receive_funding(self, grant = 50): # made up value
        self.budget_plastic_recycling += grant*len(self.households)
        
    def format_table_waste(self):
        data = {'household':[household.id for household in self.households],
                'base waste':[household.base_waste for household in self.households],
                'plastic waste':[household.plastic_waste for household in self.households]}
        df = pd.DataFrame(data)
        return df
    
    def format_table_outreach(self):
        data = {'household':[household.id for household in self.households],
                'perception':[household.perception for household in self.households],
                'knowledge':[household.knowledge for household in self.households]}
        df = pd.DataFrame(data)
        return df

    def step(self):
        print('I am {}'.format(self.id))

    def something_else(self):
        print('do something else ' + self.id)

#%% functions to initiate classes (and housesholds with it) to be changed to eleiminate randomization

def decision(probability):
    return random.random() < probability

def line(x, slope, intercept):
    return x * slope + intercept

def initialize_one_municipality(number_id, home_collection, population_distribution, budget_plastic_recycling,
                                recycling_target, priority_price_over_recycling, model):
    
    return Municipality(unique_id = 'M_{}'.format(number_id),home_collection = home_collection,
                        population_distribution = population_distribution,
                        budget_plastic_recycling = budget_plastic_recycling,
                        recycling_target = recycling_target,
                        priority_price_over_recycling = priority_price_over_recycling,
                        model = model)