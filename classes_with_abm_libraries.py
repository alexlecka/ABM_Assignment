import matplotlib.pyplot as plt
import numpy as np
import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
#load all available schedulers
import mesa.time as time


#%% Household class

class Household:
    def __init__(self, unique_id, model, household_type, perception, knowledge):
        print(unique_id)
        super().__init__(unique_id, model)
        # perception is separation, knowledge is how well we separate
        self.id = unique_id #unique id of Household example M1_H1 for Municipality 1 household 1
        self.type = household_type
        self.perception = perception
        self.knowledge = knowledge
        
    def determine_multiplier(self, h_type):
        if h_type == 'individual':
            return 1
        elif h_type == 'retired':
            return 0.8
        elif h_type == 'family':
            return 1.4
        elif h_type == 'couple':
            return 1.2
        else:
            print('Do not know this household type.')
            
    def base_waste(self, year, std_fraction = 0.1):
        waste = 40 - 0.04*year - np.exp(-0.01*year)*np.sin(0.3*year)
        mean = waste*self.determine_multiplier(self.type)
        return np.random.normal(mean, abs(mean*std_fraction))
    
    def plastic_waste_assign(self, year):
        # perception as we use it here is equal to plastic fraction
        self.plastic_waste = self.base_waste(year)*self.perception

    # Overriding of __str__ to get some useful information when calling print on household
    def __str__(self):
        return 'House id: {}'.format(self.id)

#%%
# n_households = 50
# year_range = 200
# household_types = ['individual', 'retired', 'family', 'couple']
# household_list = []
# plastic_waste_dict = {}
# for i in range(n_households):
#     plastic_waste_dict[str(i)] = []
# for i in range(n_households):
#     household_list.append(Household(random.choice(household_types), np.random.uniform(0, 1),
#                                     np.random.uniform(0, 1), i))
#     for yr in range(year_range):
#         household_list[-1].plastic_waste_assign(yr)
#         plastic_waste_dict[str(i)].append(household_list[-1].plastic_waste)
        
# #%%
#
# def assign_color(household_type):
#     if household_type == 'individual':
#         return 'red'
#     elif household_type == 'retired':
#         return 'blue'
#     elif household_type == 'family':
#         return 'green'
#     elif household_type == 'couple':
#         return 'yellow'
#
# #%%
#
# types = []
# for household in household_list:
#     types.append(household.type)
#
# heights = [types.count(household_types[0]), types.count(household_types[1]),
#            types.count(household_types[2]), types.count(household_types[3])]
# fig, ax = plt.subplots(1)
# ax.bar(np.arange(0, len(household_types)), heights, align = 'center')
# plt.xticks(np.arange(0, len(household_types)), household_types)
# plt.savefig('images/household_type_distribution.png', bbox_inches = 'tight')
# plt.show()
# plt.close()
#
# #%%
#
# from matplotlib.lines import Line2D
#
# fig, ax = plt.subplots(1, figsize = (12, 9))
# for i in range(n_households):
#     ax.plot(np.arange(0, year_range, step = 1), plastic_waste_dict[str(i)], linewidth = 0.5,
#             c = assign_color(household_list[i].type))
#
# custom_lines = [Line2D([0], [0], color = 'red', linewidth = 0.5),
#                 Line2D([0], [0], color = 'blue', linewidth = 0.5),
#                 Line2D([0], [0], color = 'green', linewidth = 0.5),
#                 Line2D([0], [0], color = 'black', linewidth = 0.5)]
#
# ax.set_xlabel('household')
# ax.set_ylabel('plastic waste (kg)')
# ax.legend(custom_lines, ['individual', 'retired', 'family', 'couple'], loc = 'best')
# plt.savefig('images/household_waste.png', bbox_inches = 'tight')
# plt.show()
# plt.close()


# %% Recycling company class

# we want technologies that improve the efficiency of recycling plastics, for
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany(Agent):
    def __init__(self, unique_id, model, init_money = 1000, init_efficiency = 0.1, price=50):
        super().__init__(unique_id, model)
#        self.budget = random.randrange(init_money) #0-1000 
        self.budget = init_money
        self.efficiency = init_efficiency
        self.price = random.randrange(price)
        self.bought_tech = []
        tech_1 = (0.15, 150, 400)
        tech_2 = (0.06, 100, 250)
        tech_3 = (0.03,70, 150)
        self.all_tech = tech_1,tech_2,tech_3
    
    def new_tech(self):
        random_gen = random.uniform(0,1)
        for i in range(len(self.all_tech)):
            n = len(self.all_tech)
            
            if self.budget > self.all_tech[i][2]: # and self.efficiency < self.model.market_analysis:
                if random_gen> i/(n*10) and random_gen<(i+1)/(n*10):
                    self.bought_tech.append(self.all_tech[i])
                    self.efficiency += self.all_tech[i][0]
                    self.price += self.all_tech[i][1]
                    self.budget = self.budget - self.all_tech[i][2]
                    self.all_tech= self.all_tech[:i]+self.all_tech[i+1:]
                    
                    break
    def step(self):
        self.new_tech()

#class Model(Model):
#    """A model with some number of agents."""
#    def __init__(self, N):
#        self.num_recycling_companies = N
#        self.schedule = RandomActivation(self)
        
        # Create agents
#       for i in range(self.num_recycling_companies):
#            a = RecyclingCompany(i, self)
#            self.schedule.add(a)
#        self.datacollector = DataCollector(
#        agent_reporters={"Budget": "budget",
#                         "Efficiency": "efficiency"})

#    def market_analysis(self):
#        company_efficiencies = [agent.efficiency for agent in self.schedule.agents]
#        x = np.mean(company_efficiencies)
#        return x
    
#    def step(self):
#        '''Advance the model by one step.'''
#        self.datacollector.collect(self)
#       self.schedule.step()

#model = Model(10)
#for i in range(50):
#    model.step()
    
#company_budget = [a.budget for a in model.schedule.agents]
#company_efficiency = [a.efficiency for a in model.schedule.agents]
#plt.hist(company_budget)
#plt.show()


#progression= model.datacollector.get_agent_vars_dataframe()


#fig, ax = plt.subplots(1, figsize = (10, 8))
#for i in range(10):
#    agent_budget = progression.xs(i, level="AgentID")
#    agent_budget.Budget.plot()

#fig, ax = plt.subplots(1, figsize = (10, 8))
#for i in range(10):
 #   agent_budget = progression.xs(i, level="AgentID")
  #  agent_budget.Efficiency.plot()

# %% Municipality class
class Municipality(Agent):
    def __init__(self, unique_id, model, number_households, home_collection, population_distribution,  budget_plastic_recycling,
        recycling_target, priority_price_over_recycling):

        # Atributes
        print(unique_id)
        super().__init__(unique_id, model)
        self.id = unique_id
        self.number_households = number_households
        self.home_collection = home_collection
        self.population_distribution = population_distribution # list [number of individual households, number of couple hh, number of family hh, number of retired hh]
        self.estimated_waste_volume = 0  # depends on households curve needs to bechecked
        self.budget_plastic_recycling = budget_plastic_recycling
        self.recycling_target = recycling_target
        self.priority_price_over_recycling = priority_price_over_recycling
        self.households = []
        self.contract = [False, None, None, None, None, None]  # active, recycling_company_id, recycling_rate, price, fee, expiration tick

        # Initiate households (Alexandra)
        temp_count = 0
        for type, type_index in zip(['individual', 'couple', 'family', 'retired'],[0,1,2,3]):

            for i in range(self.population_distribution[type_index]): # Description of population_distribution see above
                temp_perception = np.random.negative_binomial(0.5, 0.1) # this is to randomize the perception and knowledge and needs to be changed
                temp_knowledge = np.random.negative_binomial(0.5, 0.1)
                self.households.append(Household('{}_H_{}'.format(self.id,temp_count), model, type, temp_perception, temp_knowledge))

                temp_count += 1

    def __str__(self):
        return 'Municipality id: {}'.format(self.id)


    def print_all_atributes(self):
        print('id {}'.format(self.id))
        print('number households: {}'.format(self.number_households))
        print('home_collection: {}'.format(self.home_collection))
        print('population_distribution: {}'.format(self.population_distribution))
        print('estimated_waste_volume: {}'.format(self.estimated_waste_volume))
        print('budget_plastic_recycling: {}'.format(self.recycling_target))
        print('priority_price_over_recycling: {}'.format(self.priority_price_over_recycling))
        print('Households: {}'.format(self.number_households))
        print('Contract: {}'.format(self.contract))


    def request_offer(self):
        if self.contract[0] == False:
            return 'offer to come ' + self.id
        else:
            return None

    def step(self):
        print('I am {}'.format(self.id))

    def something_else(self):
        print('do something else ' + self.id)

#%% Functions to initiate classes (and housesholds with it) to be changed to eleiminate randomization
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
#                                            model = model
#                                            ))
#     return municipalities

def initialize_one_municipality(number_id, home_collection, population_distribution, budget_plastic_recycling,
                                recycling_target, priority_price_over_recycling, model):
    return Municipality(unique_id='M_{}'.format(number_id),home_collection = home_collection,
                        population_distribution = population_distribution,
                        number_households = len(population_distribution),
                        budget_plastic_recycling = budget_plastic_recycling,
                        recycling_target = recycling_target,
                        priority_price_over_recycling = priority_price_over_recycling,
                        model = model)

# %% Model

# Municipalities
# the following list represent
# [number_id, home_collection, population_distribution, budget_plastic_recycling, recycling_target, priority_price_over_recycling]
# of 10 municipalities
priority_price_over_recycling = 0.5
defined_municipalities = [[1, True,  [54, 54, 54,18], 96,  0.5, priority_price_over_recycling],
                          [2, False, [32, 24, 16, 8], 123, 0.6, priority_price_over_recycling],
                          [3, False, [7, 14, 28, 21], 126, 0.6, priority_price_over_recycling],
                          [4, True,  [60, 30, 52, 8], 107, 0.7, priority_price_over_recycling],
                          [5, True,  [0, 1, 6, 2],    136, 0.6, priority_price_over_recycling],
                          [6, False, [64, 32, 56 ,8], 109, 0.4, priority_price_over_recycling],
                          [7, False, [39, 39, 39, 13], 96, 0.7, priority_price_over_recycling],
                          [8, True,  [14, 21, 28, 7],  70, 0.5, priority_price_over_recycling],
                          [9, False, [36, 27, 18, 9], 106, 0.5, priority_price_over_recycling],
                          [10, True, [21, 21, 14, 14],120, 0.6, priority_price_over_recycling]]



class TempModel(Model):

    def __init__(self, defined_municipalities):

        # Initialization
        ## Municipality
        self.number_municipalities = len(defined_municipalities)
        self.schedule_municipalities = RandomActivation(self)
        self.schedule_households = RandomActivation(self)
        self.municipalities = []
        self.households = []
        self.offer_requests = []

        # initiate_municipalities
        for defined_municipality in defined_municipalities:
            self.municipalities.append(initialize_one_municipality(defined_municipality[0],
                                                                   defined_municipality[1],
                                                                   defined_municipality[2],
                                                                   defined_municipality[3],
                                                                   defined_municipality[4],
                                                                   defined_municipality[5], self))

        # Adding municipalities to scheduler, populating households list
        for i in range(self.number_municipalities):
            self.schedule_municipalities.add(self.municipalities[i])
            self.households = self.households + self.municipalities[i].households

        print(self.households)

        # Adding municipalities to household scheduler
        for i in range(len(self.households)):
            # print(household)
            self.schedule_households.add(self.households[i])


    def step(self):


        # Iterate in random order over municipalities
        municipalities_index_list = list(range(len(self.municipalities)))
        random.shuffle(municipalities_index_list)

        # This needs to be changed for the contract closing
        for municipality_index in municipalities_index_list:
            offer = self.municipalities[municipality_index].request_offer()

            if offer != None:
                self.offer_requests.append(offer)
        print(self.offer_requests)


# %% Testing the model

test_model = TempModel(defined_municipalities)
test_model.step()

#%% print out stuff of individuals
print(len(test_model.municipalities[2].households))
print(test_model.municipalities[2].number_households)


#%%



