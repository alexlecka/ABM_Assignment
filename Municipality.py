from Household import Household
from mesa import Agent
import pandas as pd
import random

# Variables
share_estimated_waste = 0.99 # For contract, estimated waste of municipality for contract

debugging = True
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
        self.outreach = {'learn':0, 'forget':0, 'stay':1}        
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

            # Count down the capacity tick of the company
            self.contract['recycling_company'].number_municipalities -= 1

        if self.contract['active'] == False:
            debug_print()
            debug_print('Municipality {} reports needing a new contract.'.format(self.id))

            # calculation of estimated waste volume
            # iterate over households and get current waste volume (last known to municipality)
            current_plastic_waste_mass = [household.plastic_waste for household in self.households]
            
            # 80% of the sum of this base waste is the estimated waste volume
            self.estimated_plastic_waste_mass = share_estimated_waste * sum(current_plastic_waste_mass)

            # debug_print('Municipality {} estimated_plastic_waste_mass {}.'.format(self.id, self.estimated_plastic_waste_mass))

            # just return the reference to the municipality
            return self 
        else:
            return None

    def select_offer(self, tick):
        # evaluate offers (see documentation for reasoning behind formular)
        random.shuffle(self.received_offers) # shuffling, since if there are several offers scoring equally well, always the first is selected
        scoring_offers = []
        # debug_print()
        # debug_print('Offer selection of municipality {}, options:'.format(self.id))
        # debug_print(self.received_offers)

        # Delete Companies from list that do not have capacities anymore
        offers_to_check = self.received_offers
        self.received_offers = []
        for offer in offers_to_check:
            if offer['recycling_company'].number_municipalities < offer['recycling_company'].capacity_municipalities:
                self.received_offers.append(offer)

        # Score the available offers
        for received_offer in self.received_offers:
            # calculate an offer index = evaluation 
            scoring_offers.append((self.recycling_target / received_offer['efficiency'] * received_offer ['price']) + self.priority_price_over_recycling * received_offer['price'])
        # select index of best offer
        index_best_offer = scoring_offers.index(min(scoring_offers))



        # check whether this is the very initialization
        if tick == 0:
            # if we are at the start, give the contract varied validity so that not all municipalities :
            # run out of contracts at the same time 
            expiration_tick = random.randint(1, 36)
        else:
            # otherwise contracts run for 3 years = 36 months
            expiration_tick = tick + 36

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
        
    def do_outreach(self, perception_increase = 0.02, knowledge_increase = 0.02):
        if self.outreach['stay']:
            pass
        elif self.outreach['forget']:
            for household in self.households:
                household.perception -= 0.005
                household.knowledge -= 0.005
            self.outreach['forget'] += 1
            if self.outreach['forget'] >= 4:
                self.outreach['forget'] = 0
                self.outreach['stay'] = 1
        elif self.outreach['learn']:
            for household in self.households:
                household.perception += perception_increase
                household.knowledge += knowledge_increase   
            self.outreach['learn'] = 0
            self.outreach['forget'] = 1
            self.budget_plastic_recycling -= 150 # made up value
                    
    def receive_funding(self, grant = 500): # made up value
        self.budget_plastic_recycling += grant
        
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

# def initialize_municipalities(number, home_collection_fraction = 0.5, number_households_mean = 100, number_households_sd = 20,
#                               budget_recycling_mean = 100, budget_recycling_sd = 10, recycling_target_mean = 0.5, recycling_target_sd = 0.1,
#                               priority_price_recycling_mean = 0.8, priority_price_recycling_sd = 0.1,
#                               min_share_individual_mean = 0.3, min_share_individual_sd = 0.1, model = None):
#     municipalities = []
#     for i in range(1, number + 1):
#         temp_number_householdes = np.random.normal(number_households_mean, number_households_sd)
#         temp_number_householdes = int(temp_number_householdes)
#         temp_min_share_individual = np.random.normal(min_share_individual_mean, min_share_individual_sd)
#
#         slope = (1 - 4 * temp_min_share_individual) / 6 # Ask Rapha if you want to know what it is about
#
#         distribution = [line(x, slope, temp_min_share_individual) for x in range(4)] #creating distribution on linear function
#         list_occurance = np.random.choice(4, size=temp_number_householdes, p=distribution) # draw numbers according to distribution
#         unique, count = np.unique(list_occurance, return_counts=True) # count occurance of numbers
#         temp_population_distribution = count.tolist()
#
#         municipalities.append(Municipality(unique_id = 'M_{}'.format(i),
#                                            home_collection = decision(home_collection_fraction),
#                                            population_distribution = temp_population_distribution,
#                                            number_households = temp_number_householdes,
#                                            budget_plastic_recycling = np.random.normal(budget_recycling_mean, budget_recycling_sd),
#                                            recycling_target = np.random.normal(recycling_target_mean, recycling_target_sd),
#                                            priority_price_over_recycling = np.random.normal(priority_price_recycling_mean, priority_price_recycling_sd),
#                                            model =
#                                            ))
#     return municipalities

def initialize_one_municipality(number_id, home_collection, population_distribution, budget_plastic_recycling,
                                recycling_target, priority_price_over_recycling, model):
    
    return Municipality(unique_id = 'M_{}'.format(number_id),home_collection = home_collection,
                        population_distribution = population_distribution,
                        budget_plastic_recycling = budget_plastic_recycling,
                        recycling_target = recycling_target,
                        priority_price_over_recycling = priority_price_over_recycling,
                        model = model)