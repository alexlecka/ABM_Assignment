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
defined_municipalities = [[1, True, [1, 1], 1000, 0.65, 1]]
n = 10

def salib_model(t = time_span, def_municipalities = defined_municipalities, n_municipalities = n):
    model = ABM_model(defined_municipalities, n_municipalities)
    
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

uncertainties = [IntegerParameter('n_municipalities', 1, 10)] 

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














