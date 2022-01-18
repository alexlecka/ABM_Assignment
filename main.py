from Municipality import initialize_one_municipality
from RecyclingCompany import RecyclingCompany
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from statistics import mean
from mesa import Model
import random

#%%

rapha_debug = False
alex_debug = False
debugging = False

def rapha_print(string = ''):
    if rapha_debug:
        print(string)

def alex_print(string = ''):
    if alex_debug:
        print(string)

def debug_print(string = ''):
    if debugging:
        print(string)

#%% data collector functions

def compute_recycling_rate(model):
    return model.total_recycled_plastic / model.total_potential_plastic_waste

def compute_mean_budget_municipalities(model):
    return mean([municipality.budget_plastic_recycling for municipality in model.municipalities])

def compute_mean_budget_recycling_companies(model):
    return mean([company.budget for company in model.recycling_companies])

def compute_mean_seperation_rate_households(model):
    return mean([household.perception * household.knowledge for household in model.households])

def compute_mean_recycling_efficiency_recycling_companies(model):
    return mean([company.efficiency for company in model.recycling_companies])

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

vec = [a[-1] for a in defined_municipalities]

class ABM_model(Model):

    def __init__(self, defined_municipalities, n_recycling_companies,
                 funding_municipalities,
                 improving_tech_recycling_company,
                 reverse_collection_switch = False, # Boolean True or False
                 reverse_collection_tick = 0, # time when it should be implemented
                 container_labeling_switch = False, # Boolean True or False
                 container_labeling_tick = 0, # time wehn it should be implemented
                 education_switch = False, # Boolean True or False
                 education_forgetting_frequency = 12, # Alex needs to explain this
                 perception_increase = 0.02,
                 knowledge_increase = 0.02,
                 outreach_threshold = 0.5,
                 investing_threshold = 0.5,
                 priority_price_over_recycling_vec = vec):

        debug_print('***** AGENT-BASED MODEL *****')
        debug_print('Initializing the model and the agents.')
        debug_print()
        
        # initialization
        self.funding_municipalities = funding_municipalities
        self.number_municipalities = len(defined_municipalities)
        
        self.schedule_municipalities = RandomActivation(self)
        self.schedule_households = RandomActivation(self)
        self.schedule_recycling_companies = RandomActivation(self)

        # recycling performance indicatiors
        # initialized with 1 to avoid devision by zero - all values get set to 0 at beginning of step function
        self.total_potential_plastic_waste = 1 # total mass of plastic waste present in base waste (not what ends up in plastic waste)
        self.total_plastic_waste = 1 # total mass of plastic waste that ended up in plastic waste fit for recycling
        self.total_recycled_plastic = 0 # total mass of plastic that recycling companies recycled

        # switches
        self.improving_tech_recycling_company = improving_tech_recycling_company
        self.reverse_collection_switch = reverse_collection_switch
        self.reverse_collection_tick = reverse_collection_tick
        self.container_labeling_switch = container_labeling_switch
        self.container_labeling_tick = container_labeling_tick
        self.education_switch = education_switch
        self.education_forgetting_frequency = education_forgetting_frequency
        
        self.municipalities = []
        self.households = []
        self.recycling_companies = []
        
        self.offer_requests = []
        
        self.outreach_threshold = outreach_threshold
        
        self.tick = 0

        # data collector
        self.datacollector_recycling_rate = DataCollector(
            model_reporters = {'Total recycling rate': compute_recycling_rate,
                               'Separation rate households': compute_mean_seperation_rate_households,
                               'Recycling efficiency companies': compute_mean_recycling_efficiency_recycling_companies})
        
        self.datacollector_budgets = DataCollector(
            model_reporters = {'Budget municipalities':compute_mean_budget_municipalities,
                               'Budget recycling companies': compute_mean_budget_recycling_companies})

        # necessary variables for GUI
        self.running = True

        # debug variables
        self.debug_count_fee = 0
        
        for i in range(len(defined_municipalities)):
            defined_municipalities[i][-1] = priority_price_over_recycling_vec[i]

        # initializing municipalities and households
        for defined_municipality in defined_municipalities:
            self.municipalities.append(initialize_one_municipality(defined_municipality[0],
                                                                   defined_municipality[1],
                                                                   defined_municipality[2],
                                                                   sum(defined_municipality[2])*500,
                                                                   defined_municipality[4],
                                                                   defined_municipality[5],
                                                                   perception_increase,
                                                                   knowledge_increase,
                                                                   self))

        # adding municipalities to scheduler, populating households list
        for i in range(self.number_municipalities):
            self.schedule_municipalities.add(self.municipalities[i])
            self.households = self.households + self.municipalities[i].households

        # adding municipalities to household scheduler
        for i in range(len(self.households)):
            self.schedule_households.add(self.households[i])

        # initialization of recycling companies and adding them to scheduler
        for i in range(n_recycling_companies):
            recycling_company = RecyclingCompany('R_{}'.format(i), self, investing_threshold = investing_threshold)
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

        # collect data
        self.datacollector_recycling_rate.collect(self)
        self.datacollector_budgets.collect(self)

        # reset counters
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
                municipality.receive_funding(self.funding_municipalities)
                debug_print('New budget is {}.'.format(municipality.budget_plastic_recycling))

        # households in municipalities produce waste
        for municipality in self.municipalities:
            for household in municipality.households:
                household.calc_base_waste(self.tick)
                household.calc_plastic_waste(self.tick)

                # Add potential_plastic waste to total_potential_plastic waste
                self.total_potential_plastic_waste += household.potential_plastic_waste
                self.total_plastic_waste += household.plastic_waste

        # contract closing
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

        # reset offers
        self.offer_requests = []
                
        # recycling company treats waste (recycling = selling and burning)
        # this means that a portion of the plastic waste gets recycled - first determine this amount
        for municipality in self.municipalities:
            municipality.plastic_waste = 0
            for household in municipality.households:
                municipality.plastic_waste += household.plastic_waste
            # mass of plastic whichis recycled by the recycling company is calculated here
            municipality.recyclable = municipality.plastic_waste * municipality.contract['recycling_rate']

            # add mass mass of recycled plastic to total_recycled_plastic
            self.total_recycled_plastic += municipality.recyclable
        
            # debug_print()
            # debug_print('Municipality {} produces waste out of which {} is plastic waste:'.format(municipality.id, municipality.plastic_waste))
            # data = municipality.format_table_waste()
            # alex_print(data)
        
        # check contract conditions - has municipality delivered enough plastic waste, etc.?
        for municipality in self.municipalities:            
            # 1: municipality pays for waste processing
            municipality.budget_plastic_recycling -= municipality.contract['price'] * municipality.plastic_waste

            # 2: recycling company gets paid for waste processing
            municipality.contract['recycling_company'].budget += municipality.contract['price'] * municipality.plastic_waste
            municipality.contract['recycling_company'].budget -= municipality.contract['recycling_company'].opex

            # 3: recycling company gets paid fee, in case the municipality did not deliver enough waste
            if municipality.plastic_waste < municipality.contract['minimal_plastic_waste_mass']:                
                # 3.1 the mass off the missing waste is calculated
                missing_waste = municipality.contract['minimal_plastic_waste_mass'] - municipality.plastic_waste

                # 3.2: municipality pays fee
                municipality.budget_plastic_recycling -= municipality.contract['fee'] * missing_waste

                # 3.3: recycling company gets paid the fee
                municipality.contract['recycling_company'].budget += municipality.contract['fee'] * missing_waste
                
                self.debug_count_fee += 1

            # 4: recycling company gets paid for sold recycled waste
            municipality.contract['recycling_company'].budget += (municipality.recyclable)*1.5 # 1.5 is the price per kg a company can sell

        # perform outreach based on how much budget the municipality has available
        if self.tick == 0:
            data = municipality.format_table_outreach()
            alex_print(data)

        for municipality in self.municipalities:
            if self.tick != 0:
                municipality.do_outreach('stay')
            if self.reverse_collection_switch:
                if self.tick == self.reverse_collection_tick:
                    municipality.do_outreach('reverse_waste_collection')
            if self.education_switch:
                if self.tick % self.education_forgetting_frequency == 0:
                    municipality.do_outreach('education')                
            if self.container_labeling_switch:
                if self.tick == self.container_labeling_tick:
                    municipality.do_outreach('container_labeling')
            
            data = municipality.format_table_outreach()
            alex_print(data)

        # recycling companies investing into new technologies
        # print(self.improving_tech_recycling_company)
        if self.improving_tech_recycling_company:
            for recycling_company in self.recycling_companies:
                recycling_company.new_tech()

        self.tick += 1
        
#%% testing the model

random.seed(4)

model = ABM_model(defined_municipalities, 10, 500, True)

#%%

example_i = 0

for i in range(20):
    rapha_print('Tick {}'.format(i))
    debug_print('_____________________________________________________________')
    debug_print()
    debug_print('Tick {}: municipality {} budget_plastic_recycling {}.'.format(i, model.municipalities[example_i].id, 
                                                                 model.municipalities[example_i].budget_plastic_recycling))
    debug_print('Recycling rate of total potential recyclable plastic: {}'.format(model.total_recycled_plastic / model.total_potential_plastic_waste))
    model.step()

debug_print('{} times a fee was payed'.format(model.debug_count_fee))

#%%

# data_collector = model.datacollector_recycling_rate.get_model_vars_dataframe()
# print(data_collector)

# data_collector.plot()
# plt.show()

# #%%

# data_collector_m = model.datacollector_budgets.get_model_vars_dataframe()
# print(data_collector_m)