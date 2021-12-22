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
    def __init__(self, household_type, perception, knowledge, unique_id):
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
    
n_households = 50
year_range = 200
household_types = ['individual', 'retired', 'family', 'couple']
household_list = []
plastic_waste_dict = {}
for i in range(n_households):
    plastic_waste_dict[str(i)] = []
for i in range(n_households):
    household_list.append(Household(random.choice(household_types), np.random.uniform(0, 1), 
                                    np.random.uniform(0, 1)))
    for yr in range(year_range):
        household_list[-1].plastic_waste_assign(yr)
        plastic_waste_dict[str(i)].append(household_list[-1].plastic_waste)
        
#%%
        
def assign_color(household_type):
    if household_type == 'individual':
        return 'red'
    elif household_type == 'retired':
        return 'blue'
    elif household_type == 'family':
        return 'green'
    elif household_type == 'couple':
        return 'yellow'
    
#%%

types = []
for household in household_list:
    types.append(household.type)
    
heights = [types.count(household_types[0]), types.count(household_types[1]),
           types.count(household_types[2]), types.count(household_types[3])]
fig, ax = plt.subplots(1)
ax.bar(np.arange(0, len(household_types)), heights, align = 'center')
plt.xticks(np.arange(0, len(household_types)), household_types)
plt.savefig('images/household_type_distribution.png', bbox_inches = 'tight')
plt.show()
plt.close()

#%%

from matplotlib.lines import Line2D
    
fig, ax = plt.subplots(1, figsize = (12, 9))
for i in range(n_households):
    ax.plot(np.arange(0, year_range, step = 1), plastic_waste_dict[str(i)], linewidth = 0.5, 
            c = assign_color(household_list[i].type))
    break
custom_lines = [Line2D([0], [0], color = 'red', linewidth = 0.5),
                Line2D([0], [0], color = 'blue', linewidth = 0.5),
                Line2D([0], [0], color = 'green', linewidth = 0.5),
                Line2D([0], [0], color = 'black', linewidth = 0.5)]

ax.set_xlabel('household')
ax.set_ylabel('plastic waste (kg)')
ax.legend(custom_lines, ['individual', 'retired', 'family', 'couple'], loc = 'best')
plt.savefig('images/household_waste.png', bbox_inches = 'tight')
plt.show()
plt.close()


# %% Recycling company class

# we want technologies that improve the efficiency of recycling plastics, for
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany:
    def __init__(self, init_money=1000, init_efficiency=0.1):
        self.budget = self.random.randrange(init_money)  # 0-1000
        self.efficiency = init_efficiency


# %% Municipality class
class Municipality(Agent):
    def __init__(self, unique_id, number_households, home_collection, population_distribution,  budget_plastic_recycling,
        recycling_target, priority_price_over_recycling, model):

        # Atributes
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
                self.households.append(Household(type, temp_perception, temp_knowledge, '{}_H_{}'.format(self.id,temp_count)))

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

def initialize_municipalities(number, home_collection_fraction = 0.5, number_households_mean = 100, number_households_sd = 20,
                              budget_recycling_mean = 100, budget_recycling_sd = 10, recycling_target_mean = 0.5, recycling_target_sd = 0.1,
                              priority_price_recycling_mean = 0.8, priority_price_recycling_sd = 0.1,
                              min_share_individual_mean = 0.3, min_share_individual_sd = 0.1, model = None):
    municipalities = []
    for i in range(1, number + 1):
        temp_number_householdes = np.random.normal(number_households_mean, number_households_sd)
        temp_number_householdes = int(temp_number_householdes)
        temp_min_share_individual = np.random.normal(min_share_individual_mean, min_share_individual_sd)

        slope = (1 - 4 * temp_min_share_individual) / 6 # Ask Rapha if you want to know what it is about

        distribution = [line(x, slope, temp_min_share_individual) for x in range(4)] #creating distribution on linear function
        list_occurance = np.random.choice(4, size=temp_number_householdes, p=distribution) # draw numbers according to distribution
        unique, count = np.unique(list_occurance, return_counts=True) # count occurance of numbers
        temp_population_distribution = count.tolist()

        municipalities.append(Municipality(unique_id = 'M_{}'.format(i),
                                           home_collection = decision(home_collection_fraction),
                                           population_distribution = temp_population_distribution,
                                           number_households = temp_number_householdes,
                                           budget_plastic_recycling = np.random.normal(budget_recycling_mean, budget_recycling_sd),
                                           recycling_target = np.random.normal(recycling_target_mean, recycling_target_sd),
                                           priority_price_over_recycling = np.random.normal(priority_price_recycling_mean, priority_price_recycling_sd),
                                           model = model
                                           ))
    return municipalities

# %% Model
class TempModel(Model):

    def __init__(self, number_municipalities):

        # Initialization
        ## Municipality
        self.number_municipalities = number_municipalities
        self.schedule_municipalities = RandomActivation(self)
        self.municipalities = initialize_municipalities(number_municipalities, model=self)

        self.offer_requests = []
        for i in range(self.number_municipalities):
            self.schedule_municipalities.add(self.municipalities[i])


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

test_model = TempModel(10)
test_model.step()

#%% print out stuff of individuals
print(len(test_model.municipalities[2].households))
print(test_model.municipalities[2].number_households)


#%%


