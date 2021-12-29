from Household import Household
from mesa import Agent
import random

debugging = False
def debug_print(string):
    if debugging:
        print(string)

class Municipality(Agent):
    def __init__(self, unique_id, model, number_households, home_collection, population_distribution, 
                 budget_plastic_recycling, recycling_target, priority_price_over_recycling):

        # atributes
        super().__init__(unique_id, model)
        self.id = unique_id
        self.number_households = number_households
        self.home_collection = home_collection
        self.population_distribution = population_distribution # list [number of one person households, number of multi person households]
        self.estimated_waste_volume = 0  # depends on households curve needs to be checked
        self.budget_plastic_recycling = budget_plastic_recycling
        self.recycling_target = recycling_target
        self.priority_price_over_recycling = priority_price_over_recycling
        self.households = []
        self.recyclable = 0 # mass either kg or tons
        # self.contract = [False, None, None, None, None, None]  # active, recycling_company_id, recycling_rate, price, fee, expiration tick

        self.contract = {'active' : False,
                         'recycling_company' : None,
                         'recycling_rate' : None,
                         'price' : None,
                         'fee' : None,
                         'expiration_tick' : None,
                         'minimal_waste_volume' : None}
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
        print('estimated_waste_volume: {}'.format(self.estimated_waste_volume))
        print('budget_plastic_recycling: {}'.format(self.recycling_target))
        print('priority_price_over_recycling: {}'.format(self.priority_price_over_recycling))
        print('contract: {}'.format(self.contract))

    def request_offer(self, tick):
        if tick == self.contract['expiration_tick']:
            self.contract['active'] = False
            debug_print('{} needs a new contract'.format(self.id))

        if self.contract['active'] == False:
            debug_print('and reports it')
            return self # just return the reference to the municipality
        else:
            return None

    def select_offer(self, tick):
        # evaluate offers (see documentation for reasoning behind formular)
        random.shuffle(self.received_offers) # shuffling, since if there are several offers scoring equally well, always the first is selected
        scoring_offers = []
        debug_print('this is {}'.format(self))
        debug_print(self.received_offers)

        for received_offer in self.received_offers:
            scoring_offers.append((self.recycling_target / received_offer['efficiency'] * received_offer ['price']) + self.priority_price_over_recycling * received_offer['price'])
        # select index of best offer
        index_best_offer = scoring_offers.index(min(scoring_offers))

        # check whether this is the very initialization
        if tick == 0:
            expiration_tick = random.randint(1, 36)
        else:
            expiration_tick = tick + 36

        # write contract into variable
        # self.contract = [True, self.received_offers[index_best_offer][0], self.received_offers[index_best_offer][1],
        #                  self.received_offers[index_best_offer][2], None, expiration_tick]
        self.contract['active'] = True
        self.contract['recycling_company'] = self.received_offers[index_best_offer]['recycling_company']
        self.contract['recycling_rate'] = self.received_offers[index_best_offer]['efficiency']
        self.contract['price'] = self.received_offers[index_best_offer]['price']
        self.contract['fee'] = None # needs to be changed tk
        self.contract['expiration_tick'] = expiration_tick
        self.contract['minimal_waste_volume'] = None # needs to be changed tk

        # add municipality to contract
        self.contract['municipality'] = self




        self.received_offers[index_best_offer]['recycling_company'].contract[self.id] = self.contract

        self.received_offers = []

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
                        number_households = len(population_distribution),
                        budget_plastic_recycling = budget_plastic_recycling,
                        recycling_target = recycling_target,
                        priority_price_over_recycling = priority_price_over_recycling,
                        model = model)