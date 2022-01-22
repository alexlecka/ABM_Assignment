from mesa import Agent
import random

# variables
max_capacity_municipalities = 4

#%% recycling company class

# we want technologies that improve the efficiency of recycling plastics, for
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany(Agent):

    def __init__(self, unique_id, model, init_money = 0, init_efficiency = 0.4, price = 10, opex = 100,
                 investing_threshold = 0.65):

        super().__init__(unique_id, model)
        self.id = unique_id
        
        # self.budget = random.randrange(init_money) # 0 - 1000
        self.budget = init_money
        self.efficiency = init_efficiency
        self.price = price
        self.opex = opex
        self.investing_threshold = investing_threshold
        self.number_municipalities = 0 # number of municipalities who are customers of the company
        self.capacity_municipalities = max_capacity_municipalities # maximum number of municipalities as customers
        self.bought_tech = []
        
        tech_1 = (0.15, 0.15, 80000, 20) # efficiency, increase in price per mass plastic recycled, price of the thechnology, operational expenses
        tech_2 = (0.06, 0.1, 50000, 15)
        tech_3 = (0.03, 0.08, 30000, 10)
        
        self.all_tech = tech_1, tech_2, tech_3
        self.contract = {} # a dictionary of contracts. The key is the customer (municipality) ID (not the reference)

    def provide_offer(self, offer_request):
        # company only provides offers if it has capacities
        if self.number_municipalities < self.capacity_municipalities:
            for municipality in offer_request:
                municipality.received_offers.append({'recycling_company' : self,
                                                     'efficiency' : self.efficiency,
                                                     'price' : self.price})

    def new_tech(self):
        random_gen = random.uniform(0, 1)
        for i in range(len(self.all_tech)):
            n = len(self.all_tech)
            investing_minimum_budget = self.all_tech[i][2]
            prob = random.random()
            if self.budget > investing_minimum_budget and prob < self.investing_threshold:  # and self.efficiency < self.model.market_analysis:
                if random_gen > i / (n * 10) and random_gen < (i + 1) / (n * 10):
                    self.bought_tech.append(self.all_tech[i])
                    self.efficiency += self.all_tech[i][0]
                    self.price =(1 + self.all_tech[i][1]) * self.price
                    self.opex += self.all_tech[i][3]
                    self.budget = self.budget - self.all_tech[i][2]
                    self.all_tech = self.all_tech[:i] + self.all_tech[i + 1:]
                    break

    def step(self):
        self.new_tech()

    def __str__(self):
        return 'Recycling Company ID: {}'.format(self.id)