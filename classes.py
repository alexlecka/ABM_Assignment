import matplotlib.pyplot as plt
import numpy as np
import random

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
    
    def plastic_waste(self, year):
        # perception as we use it here is equal to plastic fraction
        return self.base_waste(year)*self.perception
    
n_households = 100
household_types = ['individual', 'retired', 'family', 'couple']
household_list = []
plastic_waste = []
for i in range(n_households):
    household_list.append(Household(random.choice(household_types), np.random.uniform(0, 1), np.random.uniform(0, 1)))
    plastic_waste.append(household_list[-1].plastic_waste(1))
    
fig, ax = plt.subplots(1)
ax.scatter(np.arange(0, n_households, step = 1), plastic_waste)
ax.set_xlabel('household')
ax.set_ylabel('plastic waste (kg)')
plt.show()
plt.close()
    
#%% Municipality class    
    
# class Municipality:
#      def __init__(self):
    
#%% Recycling company class
        
# class RecyclingCompany:
#      def __init__(self):