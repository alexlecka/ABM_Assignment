import matplotlib.pyplot as plt
from mesa import Agent
import seaborn as sns
import numpy as np
import random

#%% Household class - this part is the only one used for household agent, below 
# are some examples and visualizations

class Household(Agent):
    def __init__(self, household_type, perception, knowledge):
        # perception is separation, knowledge is how well we separate
        self.type = household_type
        self.perception = perception
        self.knowledge = knowledge
        
    def starting_val(self, h_type):
        base = 40
        if h_type == 'one_person':
            return 1*base
        elif h_type == 'multi_person':
            return 2.85*base
        else:
            print('Do not know this household type.')
            
    def calc_starting_val(self):
        self.starting_value = self.starting_val(self.type)
            
    def calc_base_waste(self, t):
        waste = self.starting_value - 0.04*t - np.exp(-0.01*t)*np.sin(0.3*t)
        self.base_waste = waste
    
    def calc_plastic_waste(self, t):
        # perception as we use it here is equal to plastic fraction
        self.plastic_waste = self.base_waste*self.perception 
    
# create n_households Household objects and assign a base and plastic waste to each of them    
    
n_households = 100
time_range = 240
household_types = ['one_person', 'multi_person']
household_list = []
base_waste_dict = {}
plastic_waste_dict = {}

random.seed(3)

for i in range(n_households):
    base_waste_dict[str(i)] = []
    plastic_waste_dict[str(i)] = []
    
for i in range(n_households):
    if i < 0.39*n_households:
        household_list.append(Household('one_person', 0.5, 0.5))
    else:
        household_list.append(Household('multi_person', 0.5, 0.5))
        
    household_list[-1].calc_starting_val()
    
    for t in range(time_range):
        household_list[-1].calc_base_waste(t)
        household_list[-1].calc_plastic_waste(t)
        
        base_waste_dict[str(i)].append(household_list[-1].base_waste)
        plastic_waste_dict[str(i)].append(household_list[-1].plastic_waste)
        
#%% color assignment for visualization below
        
def assign_color(household_type):
    if household_type == 'one_person':
        return 'red'
    elif household_type == 'multi_person':
        return 'blue'
    
#%% household type distribution

sns.set_theme()

types = []
for household in household_list:
    types.append(household.type)
heights = [types.count(household_types[0]), types.count(household_types[1])]
fig, ax = plt.subplots(1)
ax.bar(np.arange(0, len(household_types)), heights, align = 'center', color = ['red', 'blue'])
plt.xticks(np.arange(0, len(household_types)), household_types)
plt.savefig('images/household_type_distribution.png', bbox_inches = 'tight')
plt.show()
plt.close()

#%% plastic waste over time for all households

from matplotlib.lines import Line2D
    
fig, ax = plt.subplots(1, figsize = (12, 9))
for i in range(n_households):
    ax.plot(np.arange(0, time_range, step = 1), base_waste_dict[str(i)], linewidth = 0.5, 
            c = assign_color(household_list[i].type))
    
custom_lines = [Line2D([0], [0], color = 'red', linewidth = 0.5),
                Line2D([0], [0], color = 'blue', linewidth = 0.5)]

ax.set_xlabel('household')
ax.set_ylabel('base waste (kg)')
ax.legend(custom_lines, ['one_person', 'multi_person'], loc = 'best')
plt.savefig('images/household_waste.png', bbox_inches = 'tight')
plt.show()
plt.close()
    
#%% Municipality class    
    
# class Municipality:
#      def __init__(self):
    
#%% Recycling company class
        
# class RecyclingCompany:
#      def __init__(self):