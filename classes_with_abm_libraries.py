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
    
#%% Municipality class    
    
# class Municipality:
#      def __init__(self):
    
#%% Recycling company class

# we want technologies that improve the efficiency of recycling plastics, for 
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany:
     def __init__(self, init_money = 1000, init_efficiency = 0.1):
         self.budget = self.random.randrange(init_money) #0-1000
         self.efficiency = init_efficiency
    
    
         