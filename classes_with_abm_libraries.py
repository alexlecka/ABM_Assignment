import matplotlib.pyplot as plt
import numpy as np
import random
from mesa import Agent, Model
from mesa.datacollection import DataCollector
#load all available schedulers
import mesa.time as time


#%% Household class

class Household:
    def __init__(self, household_type, perception, knowledge):
        # perception is separation, knowledge is how well we separate
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
    
#%% Municipality class    
    
# class Municipality:
#      def __init__(self):
    
#%% Recycling company class

# we want technologies that improve the efficiency of recycling plastics, for 
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany:
    def __init__(self, init_money = 1000, init_efficiency = 0.1, price=50):
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
            if self.budget > self.all_tech[i][2]:
                if random_gen> i/(n*10) and random_gen<(i+1)/(n*10):
                    self.bought_tech.append(self.all_tech[i])
                    self.efficiency += self.all_tech[i][0]
                    self.price += self.all_tech[i][1]
                    self.budget = self.budget - self.all_tech[i][2]
                    self.all_tech= self.all_tech[:i]+self.all_tech[i+1:]
                    
                    break



#%%
n_companies = 10
month_range = 100
init_money = 1000
company_list = []
efficiency_dict = {}
price_dict = {}
budget_dict = {}

for i in range(n_companies):
    efficiency_dict[str(i)] = []
    price_dict[str(i)] = []
    budget_dict[str(i)] = []
    
for i in range(n_companies):
    company_list.append(RecyclingCompany())
                        
    for month in range(month_range):
        company_list[-1].new_tech()
        efficiency_dict[str(i)].append(company_list[-1].efficiency)
        price_dict[str(i)].append(company_list[-1].price)
        budget_dict[str(i)].append(company_list[-1].budget)
#%%        
fig, ax = plt.subplots(1, figsize = (10, 8))
for i in range(n_companies):
    ax.plot(np.arange(0, month_range, step = 1), efficiency_dict[str(i)], linewidth = 0.5,)
    

ax.set_xlabel('months')
ax.set_ylabel('efficiency')
#ax.legend(custom_lines, ['individual', 'retired', 'family', 'couple'], loc = 'best')
#plt.savefig('images/household_waste.png', bbox_inches = 'tight')
plt.show()
plt.close()

fig, ax = plt.subplots(1, figsize = (10, 8))
for i in range(n_companies):
    ax.plot(np.arange(0, month_range, step = 1), budget_dict[str(i)], linewidth = 0.5,)
    

ax.set_xlabel('months')
ax.set_ylabel('budget (€)')
#ax.legend(custom_lines, ['individual', 'retired', 'family', 'couple'], loc = 'best')
#plt.savefig('images/household_waste.png', bbox_inches = 'tight')
plt.show()
plt.close()
      
"""
the idea is to make a list of varying technologies with different prices, 
correlation of efficiency with price and add some noise linear randomise 
efficiency offered price at the beginning create list of new technologies max capacity
"""
#%%    
tech_1 = (0.04, 100)
tech_2 = (0.06, 150)
tech_3 = (0.03,70)
all_tech = tech_1,tech_2,tech_3
budget= 500
bought_tech= []

random_gen = random.uniform(0,1)

for i in range(len(all_tech)):
    
    if budget > all_tech[i][1]:
        if random_gen> i/3 and random_gen<(i+1)/3:
            print(random_gen)
            print(all_tech[i][1])
            bought_tech.append(all_tech[i])
            all_tech = all_tech[:i]+all_tech[i+1:]
            break

print(bought_tech)
print(all_tech)         