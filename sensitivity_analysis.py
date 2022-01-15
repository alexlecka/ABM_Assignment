import pandas as pd
import numpy as np

import matplotlib.pyplot
import seaborn as sns
sns.set_style('white')

from ema_workbench.analysis.scenario_discovery_util import RuleInductionType
from ema_workbench.em_framework.salib_samplers import get_SALib_problem
from ema_workbench.em_framework.evaluators import LHS, SOBOL, MORRIS
from ema_workbench import (Model, RealParameter, TimeSeriesOutcome,
                           perform_experiments, ema_logging,Policy,
                           IntegerParameter)
from ema_workbench.analysis import feature_scoring

from SALib.analyze import sobol

from main import ABM_model
import random

#%%

time_span = 5
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
n = 10

def salib_model(t = time_span, def_municipalities = defined_municipalities,
                priority_price_over_recycling_0 = vec[0],
                priority_price_over_recycling_1 = vec[1],
                priority_price_over_recycling_2 = vec[2],
                priority_price_over_recycling_3 = vec[3],
                priority_price_over_recycling_4 = vec[4],
                priority_price_over_recycling_5 = vec[5],
                priority_price_over_recycling_6 = vec[6],
                priority_price_over_recycling_7 = vec[7],
                priority_price_over_recycling_8 = vec[8],
                priority_price_over_recycling_9 = vec[9],
                perception_increase = 0.02, knowledge_increase = 0.02,
                outreach_threshold = 0.5,
                investing_threshold = 0.5):
    
    priority_price_over_recycling_vec = [priority_price_over_recycling_0,
                                         priority_price_over_recycling_1,
                                         priority_price_over_recycling_2,
                                         priority_price_over_recycling_3,
                                         priority_price_over_recycling_4,
                                         priority_price_over_recycling_5,
                                         priority_price_over_recycling_6,
                                         priority_price_over_recycling_7,
                                         priority_price_over_recycling_8,
                                         priority_price_over_recycling_9]
    model = ABM_model(defined_municipalities, 10, priority_price_over_recycling_vec,
                      perception_increase = 0.02,
                      knowledge_increase = 0.02, 
                      outreach_threshold = 0.5,
                      investing_threshold = 0.5)
    
    plastic_waste = np.zeros((time_span, len(model.municipalities)))
    recycling_rate = np.zeros((time_span, len(model.municipalities)))
    time = np.zeros((time_span, len(model.municipalities)))
    
    for t in range(time_span):
        model.step()
        plastic_waste[t, :] = [a.plastic_waste for a in model.schedule_municipalities.agents]
        for i in range(len(model.municipalities)):
            recycling_rate[t, i] = model.municipalities[i].contract['recycling_rate']
        time[t, :] = np.full(len(model.municipalities), t + 1)
        
    print(plastic_waste)
        
    return {'TIME':time,
            'plastic_waste':plastic_waste,
            'recycling_rate':recycling_rate}

#%%

salib_model()

#%%

random.seed(4)

ema_logging.log_to_stderr(ema_logging.INFO)

uncertainties = [RealParameter('priority_price_over_recycling_0', 0, 1),
                 RealParameter('priority_price_over_recycling_1', 0, 1),
                 RealParameter('priority_price_over_recycling_2', 0, 1),
                 RealParameter('priority_price_over_recycling_3', 0, 1),
                 RealParameter('priority_price_over_recycling_4', 0, 1),
                 RealParameter('priority_price_over_recycling_5', 0, 1),
                 RealParameter('priority_price_over_recycling_6', 0, 1),
                 RealParameter('priority_price_over_recycling_7', 0, 1),
                 RealParameter('priority_price_over_recycling_8', 0, 1),
                 RealParameter('priority_price_over_recycling_9', 0, 1),
                 RealParameter('perception_increase', 0, 0.1),
                 RealParameter('knowledge_increase', 0, 0.1),
                 RealParameter('outreach_threshold', 0.2, 0.8),
                 RealParameter('investing_threshold', 0.2, 0.8)] 

outcomes = [TimeSeriesOutcome('TIME'),
            TimeSeriesOutcome('plastic_waste'),
            TimeSeriesOutcome('recycling_rate')]

py_model = Model('Python', function = salib_model)
py_model.uncertainties = uncertainties
py_model.outcomes = outcomes

#%%

n_exp = 1000

results_lhs = perform_experiments(py_model, scenarios = n_exp,
                                  uncertainty_sampling = LHS)

exp_lhs, out_lhs = results_lhs

#%%

recycling_rate_final_lhs = out_lhs['recycling_rate'][:,0,-1]
recycling_rate_mean_lhs = np.mean(out_lhs['recycling_rate'][:,0,:], axis = 1)
recycling_rate_std_lhs = np.std(out_lhs['recycling_rate'][:,0,:], axis = 1)

#%%

import statsmodels.api as sm

X = pd.DataFrame(exp_lhs).drop(['model','policy'], inplace = False, axis = 1)
X_0 = sm.add_constant(X)

est = sm.OLS(recycling_rate_final_lhs, X_0.astype(float)).fit()
print(est.summary())
print(est.params)