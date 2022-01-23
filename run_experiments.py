from ema_workbench import (Model, RealParameter, TimeSeriesOutcome,
                           ema_logging, IntegerParameter,
                           BooleanParameter)
from ema_workbench.em_framework.evaluators import LHS
from ema_workbench import MultiprocessingEvaluator
from ema_workbench import save_results
from ema_workbench import load_results
import matplotlib.pyplot as plt
from main import ABM_model
from scipy import stats
import seaborn as sns
sns.set_style('white')
import seaborn as sns
import pandas as pd
import numpy as np

#%% definition of the function that will run experiments for the time span in question

time_span = 240 # months
municipalities = [[1, True, [54, 54], 96,  0.5, 1],
                 [2, False, [32, 24], 123, 0.6, 0.1],
                 [3, False, [7, 14], 126, 0.6, 0.2],
                 [4, True, [60, 30], 107, 0.7, 0.5],
                 [5, True, [10, 1], 136, 0.6, 0.2],
                 [6, False, [64, 32], 109, 0.4, 0.7],
                 [7, False, [39, 39], 96, 0.7, 0.3],
                 [8, True, [14, 21], 70, 0.5, 0.6],
                 [9, False, [36, 27], 106, 0.5, 0.5],
                 [10, True, [21, 21], 120, 0.6, 0.4]]

vec = [a[-1] for a in municipalities]

def experiment(t = time_span,
               defined_municipalities = municipalities, # the municipalities belonging to the agent-based model
               n_recycling_companies = 10, # number of recycling companies to be considered in the agent-based model
               funding_municipalities = 50, # annual funding municipalities receive
               improving_tech_recycling_company = True, # bool True or False
               reverse_collection_switch = True, # boolean True or False
               reverse_collection_tick = 0, # time when it should be implemented
               container_labeling_switch = True, # boolean True or False
               container_labeling_tick = 0, # time wehn it should be implemented
               education_switch = True, # boolean True or False
               education_frequency = 12, # municipality will try invest into education every this many months
               investing_threshold = 0.5, # recycling company will (not) invest into new technology 
               priority_price_over_recycling_mean = 0.5):
    
    priority_price_over_recycling_vec = stats.truncnorm.rvs(0.2, 0.8, 
                                                            loc = priority_price_over_recycling_mean, 
                                                            scale = 0.2,
                                                            size = 10)
    
    model = ABM_model(defined_municipalities, 
                      n_recycling_companies, 
                      funding_municipalities,  
                      improving_tech_recycling_company,
                      reverse_collection_switch,
                      reverse_collection_tick,
                      container_labeling_switch,
                      container_labeling_tick,
                      education_switch,
                      education_frequency,
                      0.5,
                      priority_price_over_recycling_vec)
    
    # defining outcomes of the experiment (dependent variables)
    time = np.zeros(t)
    plastic_fraction = np.zeros(t)
    
    M0_budget = np.zeros(t)
    M1_budget = np.zeros(t)
    M2_budget = np.zeros(t)
    M3_budget = np.zeros(t)
    M4_budget = np.zeros(t)
    M5_budget = np.zeros(t)
    M6_budget = np.zeros(t)
    M7_budget = np.zeros(t)
    M8_budget = np.zeros(t)
    M9_budget = np.zeros(t)
    M_budget = [M0_budget, M1_budget, M2_budget,
                M3_budget, M4_budget, M5_budget,
                M6_budget, M7_budget, M8_budget,
                M9_budget]
    
    M0_perception_mean = np.zeros(t)
    M1_perception_mean = np.zeros(t)
    M2_perception_mean = np.zeros(t)
    M3_perception_mean = np.zeros(t)
    M4_perception_mean = np.zeros(t)
    M5_perception_mean = np.zeros(t)
    M6_perception_mean = np.zeros(t)
    M7_perception_mean = np.zeros(t)
    M8_perception_mean = np.zeros(t)
    M9_perception_mean = np.zeros(t)
    M_perception_mean = [M0_perception_mean, M1_perception_mean,
                         M2_perception_mean, M3_perception_mean,
                         M4_perception_mean, M5_perception_mean,
                         M6_perception_mean, M7_perception_mean,
                         M8_perception_mean, M9_perception_mean]
    
    M0_knowledge_mean = np.zeros(t)
    M1_knowledge_mean = np.zeros(t)
    M2_knowledge_mean = np.zeros(t)
    M3_knowledge_mean = np.zeros(t)
    M4_knowledge_mean = np.zeros(t)
    M5_knowledge_mean = np.zeros(t)
    M6_knowledge_mean = np.zeros(t)
    M7_knowledge_mean = np.zeros(t)
    M8_knowledge_mean = np.zeros(t)
    M9_knowledge_mean = np.zeros(t)
    M_knowledge_mean = [M0_knowledge_mean, M1_knowledge_mean,
                        M2_knowledge_mean, M3_knowledge_mean,
                        M4_knowledge_mean, M5_knowledge_mean,
                        M6_knowledge_mean, M7_knowledge_mean,
                        M8_knowledge_mean, M9_knowledge_mean]
    
    R0_budget = np.zeros(t)
    R1_budget = np.zeros(t)
    R2_budget = np.zeros(t)
    R3_budget = np.zeros(t)
    R4_budget = np.zeros(t)
    R5_budget = np.zeros(t)
    R6_budget = np.zeros(t)
    R7_budget = np.zeros(t)
    R8_budget = np.zeros(t)
    R9_budget = np.zeros(t)
    R_budget = [R0_budget, R1_budget, R2_budget,
                R3_budget, R4_budget, R5_budget,
                R6_budget, R7_budget, R8_budget,
                R9_budget]
    
    # calculating the outcomes
    for time_step in range(t):
        time[time_step] = time_step
        plastic_fraction[time_step] = model.total_recycled_plastic/model.total_potential_plastic_waste
        
        for municipality, recycling_company, i in zip(model.municipalities, model.recycling_companies, range(len(model.municipalities))):
            M_budget[i][time_step] = municipality.budget_plastic_recycling
            
            all_perception = [a.perception for a in municipality.households]
            M_perception_mean[i][time_step] = np.mean(all_perception)
            
            all_knowledge = [a.knowledge for a in municipality.households]
            M_knowledge_mean[i][time_step] = np.mean(all_knowledge)
            
            if i < n_recycling_companies:
                R_budget[i][time_step] = recycling_company.budget
        
        model.step()
        
    # return outcomes    
    return {'time':time,
            'recycling_rate':plastic_fraction,
            'M0_budget':M0_budget,
            'M1_budget':M1_budget,
            'M2_budget':M2_budget,
            'M3_budget':M3_budget,
            'M4_budget':M4_budget,
            'M5_budget':M5_budget,
            'M6_budget':M6_budget, 
            'M7_budget':M7_budget, 
            'M8_budget':M8_budget,
            'M9_budget':M9_budget,
            'M0_perception_mean':M0_perception_mean,
            'M1_perception_mean':M1_perception_mean,
            'M2_perception_mean':M2_perception_mean,
            'M3_perception_mean':M3_perception_mean,
            'M4_perception_mean':M4_perception_mean,
            'M5_perception_mean':M5_perception_mean,
            'M6_perception_mean':M6_perception_mean,
            'M7_perception_mean':M7_perception_mean,
            'M8_perception_mean':M8_perception_mean,
            'M9_perception_mean':M9_perception_mean,
            'M0_knowledge_mean':M0_knowledge_mean,
            'M1_knowledge_mean':M1_knowledge_mean,
            'M2_knowledge_mean':M2_knowledge_mean,
            'M3_knowledge_mean':M3_knowledge_mean,
            'M4_knowledge_mean':M4_knowledge_mean,
            'M5_knowledge_mean':M5_knowledge_mean,
            'M6_knowledge_mean':M6_knowledge_mean,
            'M7_knowledge_mean':M7_knowledge_mean,
            'M8_knowledge_mean':M8_knowledge_mean,
            'M9_knowledge_mean':M9_knowledge_mean,
            'R0_budget':R0_budget,
            'R1_budget':R1_budget,
            'R2_budget':R2_budget,
            'R3_budget':R3_budget,
            'R4_budget':R4_budget,
            'R5_budget':R5_budget,
            'R6_budget':R6_budget, 
            'R7_budget':R7_budget, 
            'R8_budget':R8_budget,
            'R9_budget':R9_budget}

#%%

experiment()

#%%

ema_logging.log_to_stderr(ema_logging.INFO)

uncertainties = [IntegerParameter('n_recycling_companies', 4, 10), 
                 IntegerParameter('funding_municipalities', 90, 100),
                 BooleanParameter('improving_tech_recycling_company'),
                 BooleanParameter('reverse_collection_switch'),
                 IntegerParameter('reverse_collection_tick', 0, 239),
                 BooleanParameter('container_labeling_switch'),
                 IntegerParameter('container_labeling_tick', 0, 239),
                 BooleanParameter('education_switch'),
                 IntegerParameter('education_frequency', 12, 48),
                 RealParameter('investing_threshold', 0, 1),
                 RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

outcomes = [TimeSeriesOutcome('time'),
            TimeSeriesOutcome('recycling_rate'),
            TimeSeriesOutcome('M0_budget'),
            TimeSeriesOutcome('M1_budget'),
            TimeSeriesOutcome('M2_budget'),
            TimeSeriesOutcome('M3_budget'),
            TimeSeriesOutcome('M4_budget'),
            TimeSeriesOutcome('M5_budget'),
            TimeSeriesOutcome('M6_budget'), 
            TimeSeriesOutcome('M7_budget'), 
            TimeSeriesOutcome('M8_budget'),
            TimeSeriesOutcome('M9_budget'),
            TimeSeriesOutcome('M0_perception_mean'),
            TimeSeriesOutcome('M1_perception_mean'),
            TimeSeriesOutcome('M2_perception_mean'),
            TimeSeriesOutcome('M3_perception_mean'),
            TimeSeriesOutcome('M4_perception_mean'),
            TimeSeriesOutcome('M5_perception_mean'),
            TimeSeriesOutcome('M6_perception_mean'),
            TimeSeriesOutcome('M7_perception_mean'),
            TimeSeriesOutcome('M8_perception_mean'),
            TimeSeriesOutcome('M9_perception_mean'),
            TimeSeriesOutcome('M0_knowledge_mean'),
            TimeSeriesOutcome('M1_knowledge_mean'),
            TimeSeriesOutcome('M2_knowledge_mean'),
            TimeSeriesOutcome('M3_knowledge_mean'),
            TimeSeriesOutcome('M4_knowledge_mean'),
            TimeSeriesOutcome('M5_knowledge_mean'),
            TimeSeriesOutcome('M6_knowledge_mean'),
            TimeSeriesOutcome('M7_knowledge_mean'),
            TimeSeriesOutcome('M8_knowledge_mean'),
            TimeSeriesOutcome('M9_knowledge_mean'),
            TimeSeriesOutcome('R0_budget'),
            TimeSeriesOutcome('R1_budget'),
            TimeSeriesOutcome('R2_budget'),
            TimeSeriesOutcome('R3_budget'),
            TimeSeriesOutcome('R4_budget'),
            TimeSeriesOutcome('R5_budget'),
            TimeSeriesOutcome('R6_budget'), 
            TimeSeriesOutcome('R7_budget'), 
            TimeSeriesOutcome('R8_budget'),
            TimeSeriesOutcome('R9_budget')]

#%% experiment design

n_exp = 100

#%% scenario 1 - no policy, no investment

uncertainties_scenario1 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario1 = Model('Python', function = experiment)
scenario1.uncertainties = uncertainties_scenario1
scenario1.outcomes = outcomes

with MultiprocessingEvaluator(scenario1) as evaluator:
    results_scenario1 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario1, out_scenario1 = results_scenario1

# save_results(results_scenario1, 'results_scenario1.tar.gz')

#%% scenario 2 - no policy, investment

# CHANGE improving_tech_recycling_company TO TRUE IN experiment DEFINITION

uncertainties_scenario2 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           RealParameter('investing_threshold', 0, 1),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario2 = Model('Python', function = experiment)
scenario2.uncertainties = uncertainties_scenario2
scenario2.outcomes = outcomes

with MultiprocessingEvaluator(scenario2) as evaluator:
    results_scenario2 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario2, out_scenario2 = results_scenario2

# save_results(results_scenario2, 'results_scenario2.tar.gz')

#%% scenario 3 - policy 1, no investment

# CHANGE improving_tech_recycling_company TO FALSE IN experiment DEFINITION
# CHANGE reverse_collection_switch TO TRUE IN experiment DEFINITION

uncertainties_scenario3 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('reverse_collection_tick', 0, 239),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario3 = Model('Python', function = experiment)
scenario3.uncertainties = uncertainties_scenario3
scenario3.outcomes = outcomes

with MultiprocessingEvaluator(scenario3) as evaluator:
    results_scenario3 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario3, out_scenario3 = results_scenario3

# save_results(results_scenario3, 'results_scenario3.tar.gz')

#%% scenario 4 - policy 1, investment

# CHANGE improving_tech_recycling_company TO TRUE IN experiment DEFINITION

uncertainties_scenario4 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('reverse_collection_tick', 0, 239),
                           RealParameter('investing_threshold', 0, 1),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario4 = Model('Python', function = experiment)
scenario4.uncertainties = uncertainties_scenario4
scenario4.outcomes = outcomes

with MultiprocessingEvaluator(scenario4) as evaluator:
    results_scenario4 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario4, out_scenario4 = results_scenario4

# save_results(results_scenario4, 'results_scenario4.tar.gz')

#%% scenario 5 - policy 2, no investment

# CHANGE improving_tech_recycling_company TO FALSE IN experiment DEFINITION
# CHANGE reverse_collection_switch TO FALSE IN experiment DEFINITION
# CHANGE container_labeling_switch TO TRUE IN experiment DEFINITION

uncertainties_scenario5 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('container_labeling_tick', 0, 239),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario5 = Model('Python', function = experiment)
scenario5.uncertainties = uncertainties_scenario5
scenario5.outcomes = outcomes

with MultiprocessingEvaluator(scenario5) as evaluator:
    results_scenario5 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario5, out_scenario5 = results_scenario5

# save_results(results_scenario5, 'results_scenario5.tar.gz')

#%% scenario 6 - policy 2, investment

# CHANGE improving_tech_recycling_company TO TRUE IN experiment DEFINITION

uncertainties_scenario6 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('container_labeling_tick', 0, 239),
                           RealParameter('investing_threshold', 0, 1),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario6 = Model('Python', function = experiment)
scenario6.uncertainties = uncertainties_scenario6
scenario6.outcomes = outcomes

with MultiprocessingEvaluator(scenario6) as evaluator:
    results_scenario6 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario6, out_scenario6 = results_scenario6

# save_results(results_scenario6, 'results_scenario6.tar.gz')

#%% scenario 7 - policy 3, no investment

# CHANGE improving_tech_recycling_company TO FALSE IN experiment DEFINITION
# CHANGE container_labeling_switch TO FALSE IN experiment DEFINITION
# CHANGE education_switch TO TRUE IN experiment DEFINITION

uncertainties_scenario7 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('education_frequency', 12, 48),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario7 = Model('Python', function = experiment)
scenario7.uncertainties = uncertainties_scenario7
scenario7.outcomes = outcomes

with MultiprocessingEvaluator(scenario7) as evaluator:
    results_scenario7 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario7, out_scenario7 = results_scenario7

# save_results(results_scenario7, 'results_scenario7.tar.gz')

#%% scenario 8 - policy 3, investment

# CHANGE improving_tech_recycling_company TO TRUE IN experiment DEFINITION

uncertainties_scenario8 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('education_frequency', 12, 48),
                           RealParameter('investing_threshold', 0, 1),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario8 = Model('Python', function = experiment)
scenario8.uncertainties = uncertainties_scenario8
scenario8.outcomes = outcomes

with MultiprocessingEvaluator(scenario8) as evaluator:
    results_scenario8 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario8, out_scenario8 = results_scenario8

# save_results(results_scenario8, 'results_scenario8.tar.gz')

#%% scenario 9 - all 3 policies, no investment

# CHANGE improving_tech_recycling_company TO FALSE IN experiment DEFINITION
# CHANGE reverse_collection_switch TO TRUE IN experiment DEFINITION
# CHANGE container_labeling_switch TO TRUE IN experiment DEFINITION

uncertainties_scenario9 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('reverse_collection_tick', 0, 239),
                           IntegerParameter('container_labeling_tick', 0, 239),
                           IntegerParameter('education_frequency', 12, 48),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario9 = Model('Python', function = experiment)
scenario9.uncertainties = uncertainties_scenario9
scenario9.outcomes = outcomes

with MultiprocessingEvaluator(scenario9) as evaluator:
    results_scenario9 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario9, out_scenario9 = results_scenario9

save_results(results_scenario9, 'results_scenario9.tar.gz')

#%% scenario 10 - all 3 policies, investment

# CHANGE improving_tech_recycling_company TO TRUE IN experiment DEFINITION

uncertainties_scenario10 = [IntegerParameter('n_recycling_companies', 4, 10), 
                           IntegerParameter('funding_municipalities', 1750, 2250),
                           IntegerParameter('reverse_collection_tick', 0, 239),
                           IntegerParameter('container_labeling_tick', 0, 239),
                           IntegerParameter('education_frequency', 12, 48),
                           RealParameter('investing_threshold', 0, 1),
                           RealParameter('priority_price_over_recycling_mean', 0.2, 0.8)]

scenario10 = Model('Python', function = experiment)
scenario10.uncertainties = uncertainties_scenario10
scenario10.outcomes = outcomes

with MultiprocessingEvaluator(scenario10) as evaluator:
    results_scenario10 = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_scenario10, out_scenario10 = results_scenario10

# save_results(results_scenario10, 'results_scenario10.tar.gz')

#%% load and merge results

path = '../data/'

results_scenario1 = load_results(path + 'results_scenario1.tar.gz')
exp_scenario1, out_scenario1 = results_scenario1
results_scenario2 = load_results(path + 'results_scenario2.tar.gz')
exp_scenario2, out_scenario2 = results_scenario2
results_scenario3 = load_results(path + 'results_scenario3.tar.gz')
exp_scenario3, out_scenario3 = results_scenario3
results_scenario4 = load_results(path + 'results_scenario4.tar.gz')
exp_scenario4, out_scenario4 = results_scenario4
results_scenario5 = load_results(path + 'results_scenario5.tar.gz')
exp_scenario5, out_scenario5 = results_scenario5
results_scenario6 = load_results(path + 'results_scenario6.tar.gz')
exp_scenario6, out_scenario6 = results_scenario6
results_scenario7 = load_results(path + 'results_scenario7.tar.gz')
exp_scenario7, out_scenario7 = results_scenario7
results_scenario8 = load_results(path + 'results_scenario8.tar.gz')
exp_scenario8, out_scenario8 = results_scenario8
results_scenario9 = load_results(path + 'results_scenario9.tar.gz')
exp_scenario9, out_scenario9 = results_scenario9
results_scenario10 = load_results(path + 'results_scenario10.tar.gz')
exp_scenario10, out_scenario10 = results_scenario10

#%% plot for recycling rates

x_time = np.arange(0, time_span)
labels = ['scenario1', 'scenario2', 'scenario3', 'scenario4',
          'scenario5', 'scenario6', 'scenario7', 'scenario8',
          'scenario9', 'scenario10']
recycling_rate_scenario1 = []
recycling_rate_scenario2 = []
recycling_rate_scenario3 = []
recycling_rate_scenario4 = []
recycling_rate_scenario5 = []
recycling_rate_scenario6 = []
recycling_rate_scenario7 = []
recycling_rate_scenario8 = []
recycling_rate_scenario9 = []
recycling_rate_scenario10 = []
for i in range(len(x_time)):
    recycling_rate_scenario1.append(np.mean(out_scenario1['recycling_rate'][:, i]))
    recycling_rate_scenario2.append(np.mean(out_scenario2['recycling_rate'][:, i]))
    recycling_rate_scenario3.append(np.mean(out_scenario3['recycling_rate'][:, i]))
    recycling_rate_scenario4.append(np.mean(out_scenario4['recycling_rate'][:, i]))
    recycling_rate_scenario5.append(np.mean(out_scenario5['recycling_rate'][:, i]))
    recycling_rate_scenario6.append(np.mean(out_scenario6['recycling_rate'][:, i]))
    recycling_rate_scenario7.append(np.mean(out_scenario7['recycling_rate'][:, i]))
    recycling_rate_scenario8.append(np.mean(out_scenario8['recycling_rate'][:, i]))
    recycling_rate_scenario9.append(np.mean(out_scenario9['recycling_rate'][:, i]))
    recycling_rate_scenario10.append(np.mean(out_scenario10['recycling_rate'][:, i]))
recycling_rates = [recycling_rate_scenario1, recycling_rate_scenario2,
                   recycling_rate_scenario3, recycling_rate_scenario4,
                   recycling_rate_scenario5, recycling_rate_scenario6, 
                   recycling_rate_scenario7, recycling_rate_scenario8,
                   recycling_rate_scenario9, recycling_rate_scenario10]

colors = []
sns.set_theme()
fig, ax = plt.subplots(1)
for data, i in zip(recycling_rates, range(len(recycling_rates))):
    p = ax.plot(x_time, data, label = labels[i])
    colors.append(p[0].get_color())
ax.set_xlabel('time step')
ax.set_ylabel('average recycling rate')
plt.legend(bbox_to_anchor = (0.98, -0.2), ncol = 3)
plt.show()
plt.close()

#%% separate plots for report

fig, ax = plt.subplots(3, 2, figsize = (14, 8))
for i, axis in enumerate(fig.axes):
    if i == 5:
        for data, j in zip(recycling_rates, range(len(recycling_rates))):
            axis.plot(x_time, data, label = labels[j])
            axis.legend(bbox_to_anchor = (1, -0.35), ncol = 5)
            axis.set_title('combined plot', y = 1, pad = -14, loc = 'left')
    else:
        axis.plot(x_time, recycling_rates[i*2], label = labels[i*2], color = colors[i*2])
        axis.plot(x_time, recycling_rates[i*2 + 1], label = labels[i*2 + 1], color = colors[i*2 + 1])
        axis.set_title(i + 1, y = 1, pad = -14, loc = 'left')
    axis.set_xlabel('time step (month)')
    axis.set_ylabel('average\nrecycling rate')
    axis.set_ylim(0.05, 0.6)
plt.show()
plt.close()

#%% scatter plot final recycling rate vs final budget

final_recycling_rate_scenario1 = [out_scenario1['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario2 = [out_scenario2['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario3 = [out_scenario3['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario4 = [out_scenario4['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario5 = [out_scenario5['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario6 = [out_scenario6['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario7 = [out_scenario7['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario8 = [out_scenario8['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario9 = [out_scenario9['recycling_rate'][i, -1] for i in range(n_exp)]
final_recycling_rate_scenario10 = [out_scenario10['recycling_rate'][i, -1] for i in range(n_exp)]

keys = ['M0_budget', 'M1_budget', 'M2_budget', 'M3_budget', 'M4_budget',
        'M5_budget', 'M6_budget', 'M7_budget', 'M8_budget', 'M9_budget']
final_M_budget_scenario1 =  [np.mean([out_scenario1[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario2 =  [np.mean([out_scenario2[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario3 =  [np.mean([out_scenario3[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario4 =  [np.mean([out_scenario4[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario5 =  [np.mean([out_scenario5[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario6 =  [np.mean([out_scenario6[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario7 =  [np.mean([out_scenario7[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario8 =  [np.mean([out_scenario8[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario9 =  [np.mean([out_scenario9[key][i, -1] for key in keys]) for i in range(n_exp)]
final_M_budget_scenario10 =  [np.mean([out_scenario10[key][i, -1] for key in keys]) for i in range(n_exp)]

data = {'final_recycling_rate_scenario1':final_recycling_rate_scenario1,
        'final_recycling_rate_scenario2':final_recycling_rate_scenario2,
        'final_recycling_rate_scenario3':final_recycling_rate_scenario3,
        'final_recycling_rate_scenario4':final_recycling_rate_scenario4,
        'final_recycling_rate_scenario5':final_recycling_rate_scenario5,
        'final_recycling_rate_scenario6':final_recycling_rate_scenario6,
        'final_recycling_rate_scenario7':final_recycling_rate_scenario7,
        'final_recycling_rate_scenario8':final_recycling_rate_scenario8,
        'final_recycling_rate_scenario9':final_recycling_rate_scenario9,
        'final_recycling_rate_scenario10':final_recycling_rate_scenario10,
        'final_M_budget_scenario1':final_M_budget_scenario1,
        'final_M_budget_scenario2':final_M_budget_scenario2,
        'final_M_budget_scenario3':final_M_budget_scenario3,
        'final_M_budget_scenario4':final_M_budget_scenario4,
        'final_M_budget_scenario5':final_M_budget_scenario5,
        'final_M_budget_scenario6':final_M_budget_scenario6,
        'final_M_budget_scenario7':final_M_budget_scenario7,
        'final_M_budget_scenario8':final_M_budget_scenario8,
        'final_M_budget_scenario9':final_M_budget_scenario9,
        'final_M_budget_scenario10':final_M_budget_scenario10}

df = pd.DataFrame(data)

#%%

sns.set_theme()
fig, ax = plt.subplots(1)
for i in range(1, 11):
    ax.scatter(np.mean(data['final_recycling_rate_scenario{}'.format(i)]),
               np.mean(data['final_M_budget_scenario{}'.format(i)]), label = 'scenario{}'.format(i))
ax.set_xlabel('final recycling rate')
ax.set_ylabel('final budget')
plt.legend(bbox_to_anchor = (0.98, -0.2), ncol = 3)
plt.show()
plt.close()






    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    