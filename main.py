from Municipality import initialize_one_municipality
from RecyclingCompany import RecyclingCompany
from mesa.datacollection import DataCollector
from statistics import mean
from mesa import Model
import random

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

def budget_municipality_getter(index):
    def budget_municipality(model):
        return model.municipalities[index].budget_plastic_recycling
    return budget_municipality

def budget_recycling_companies_getter(index):
    def budget_recycling(model):
        print(len(model.recycling_companies))
        return model.recycling_companies[index].budget
    return budget_recycling


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

vec = [a[-1] for a in defined_municipalities]

class ABM_model(Model):

    def __init__(self, 
                 defined_municipalities, # the municipalities belonging to the agent-based model
                 n_recycling_companies = 10, # number of recycling companies to be considered in the agent-based model
                 funding_municipalities = 50, # annual funding municipalities receive
                 improving_tech_recycling_company = False, # bool True or False
                 reverse_collection_switch = False, # boolean True or False
                 reverse_collection_tick = 0, # time when it should be implemented
                 container_labeling_switch = False, # boolean True or False
                 container_labeling_tick = 0, # time wehn it should be implemented
                 education_switch = False, # boolean True or False
                 education_frequency = 12, # municipality will try invest into education every this many months
                 investing_threshold = 0.5, # recycling company will (not) invest into new technology 
                 priority_price_over_recycling_vec = vec):
        
        self.tick = 0
        
        # initialization of municipalities and households        
        self.municipalities = []
        self.households = []
        self.recycling_companies = []
        
        for defined_municipality in defined_municipalities:
            self.municipalities.append(initialize_one_municipality(defined_municipality[0],
                                                                   defined_municipality[1],
                                                                   defined_municipality[2],
                                                                   sum(defined_municipality[2])* funding_municipalities,
                                                                   defined_municipality[4],
                                                                   defined_municipality[5],
                                                                   self))
            
        for i in range(n_recycling_companies):
            recycling_company = RecyclingCompany('R_{}'.format(i), self, investing_threshold = investing_threshold)
            self.recycling_companies.append(recycling_company)
        
        self.funding_municipalities = funding_municipalities
        
        # switches
        self.improving_tech_recycling_company = improving_tech_recycling_company
        self.reverse_collection_switch = reverse_collection_switch
        self.reverse_collection_tick = reverse_collection_tick
        self.container_labeling_switch = container_labeling_switch
        self.container_labeling_tick = container_labeling_tick
        self.education_switch = education_switch
        self.education_frequency = education_frequency 
        
        self.investing_threshold = investing_threshold
        
        for i in range(len(defined_municipalities)):
            defined_municipalities[i][-1] = priority_price_over_recycling_vec[i]

        # recycling performance indicatiors
        # initialized with 1 to avoid devision by zero - all values get set to 0 at beginning of step function
        self.total_potential_plastic_waste = 1 # total mass of plastic waste present in base waste (not what ends up in plastic waste)
        self.total_plastic_waste = 1 # total mass of plastic waste that ended up in plastic waste fit for recycling
        self.total_recycled_plastic = 0 # total mass of plastic that recycling companies recycled
        
        self.offer_requests = []

        # data collectors
        # self.datacollector_recycling_rate = DataCollector(
        #     model_reporters = {'Total recycling rate': compute_recycling_rate,
        #                        'Separation rate households': compute_mean_seperation_rate_households,
        #                        'Recycling efficiency companies': compute_mean_recycling_efficiency_recycling_companies})
        
        # self.datacollector_budgets = DataCollector(
        #     model_reporters = {'Budget municipalities':compute_mean_budget_municipalities,
        #                        'Budget recycling companies': compute_mean_budget_recycling_companies})

        # municipalities_dic = {}
        # for i in range(len(self.municipalities)):
        #     municipalities_dic['M{} recycling budget'.format(i + 1)] = budget_municipality_getter(i)

        # self.datacollector_budget_municipality = DataCollector(
        #     model_reporters= municipalities_dic)

        # recycling_companies_dic = {}
        # for i in range(len(self.recycling_companies)):
        #     recycling_companies_dic['R{} budget'.format(i + 1)] = budget_recycling_companies_getter(i)

        # self.datacollector_budget_recycling_companies = DataCollector(
        #     model_reporters=recycling_companies_dic)

        # necessary variables for GUI
        self.running = True

    def step(self):
        
        # reset counters
        self.total_potential_plastic_waste = 1
        self.total_plastic_waste = 1
        self.total_recycled_plastic = 0

        # iterate in random order over municipalities to establish order
        municipalities_index_list = list(range(len(self.municipalities)))
        random.shuffle(municipalities_index_list)
        
        # municipalities receive funding if it is the start of the year
        if self.tick%12 == 0:
            for municipality in self.municipalities:
                municipality.receive_funding(self.funding_municipalities)

        # households in municipalities produce waste
        for municipality in self.municipalities:
            for household in municipality.households:
                household.calc_base_waste(self.tick)
                household.calc_plastic_waste(self.tick)

                # add potential_plastic waste to total_potential_plastic waste
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
                
            # 4: recycling company gets paid for sold recycled waste
            municipality.contract['recycling_company'].budget += (municipality.recyclable)*1.5 # 1.5 is the price per kg a company can sell

        # perform outreach based on how much budget the municipality has available
        for municipality in self.municipalities:
            if self.tick != 0 and self.education_switch:
                municipality.do_outreach('stay')
            if self.reverse_collection_switch:
                if self.tick == self.reverse_collection_tick:
                    municipality.do_outreach('reverse_waste_collection')
            if self.education_switch:
                if self.tick % self.education_frequency == 0:
                    municipality.do_outreach('education')                
            if self.container_labeling_switch:
                if self.tick == self.container_labeling_tick:
                    municipality.do_outreach('container_labeling')

        # recycling companies investing into new technologies
        # print(self.improving_tech_recycling_company)
        if self.improving_tech_recycling_company:
            for recycling_company in self.recycling_companies:
                recycling_company.new_tech()

        # collect data
        # self.datacollector_recycling_rate.collect(self)
        # self.datacollector_budgets.collect(self)
        # self.datacollector_budget_municipality.collect(self)
        # self.datacollector_budget_recycling_companies.collect(self)

        self.tick += 1
        
#%% testing the model

random.seed(4)

model = ABM_model(defined_municipalities, 10, 500, True)

#%%

# data_collector = model.datacollector_recycling_rate.get_model_vars_dataframe()
# print(data_collector)

# data_collector.plot()
# plt.show()

# #%%

# data_collector_m = model.datacollector_budgets.get_model_vars_dataframe()
# print(data_collector_m)