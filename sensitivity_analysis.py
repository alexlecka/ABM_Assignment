from ema_workbench.analysis.scenario_discovery_util import RuleInductionType
from ema_workbench.em_framework.salib_samplers import get_SALib_problem
from ema_workbench.em_framework.evaluators import LHS, SOBOL
from ema_workbench import (Model, RealParameter, TimeSeriesOutcome,
                           perform_experiments, ema_logging,
                           IntegerParameter, BooleanParameter)
from ema_workbench.analysis import feature_scoring
from ema_workbench import MultiprocessingEvaluator
from ema_workbench.analysis import prim
import matplotlib.pyplot as plt
from SALib.analyze import sobol 
from main import ABM_model
from scipy import stats
import seaborn as sns
sns.set_style('white')
import seaborn as sns
import pandas as pd
import numpy as np

#%%

time_span = 240 # running the model for 240 months - 20 years
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

def ema_model(t = time_span, 
                defined_municipalities_in = defined_municipalities,
                n_recycling_companies_in = 10,        
                funding_municipalities_in = 50,
                improving_tech_recycling_company_in = False,
                reverse_collection_switch_in = True,
                reverse_collection_tick_in = 100,
                container_labeling_switch_in = True,
                container_labeling_tick_in = 100,
                education_switch_in = True,
                education_frequency_in = 12,
                priority_price_over_recycling_mean_in = 0.5,
                investing_threshold = 0.5):
    
    priority_price_over_recycling_vec = stats.truncnorm.rvs(0, 1, 
                                                            loc = priority_price_over_recycling_mean_in, 
                                                            scale = 0.2,
                                                            size = 10)
    
    model = ABM_model(defined_municipalities, 
                      n_recycling_companies = n_recycling_companies_in, 
                      funding_municipalities = funding_municipalities_in,  
                      improving_tech_recycling_company = improving_tech_recycling_company_in,
                      reverse_collection_switch = reverse_collection_switch_in,
                      reverse_collection_tick = reverse_collection_tick_in,
                      container_labeling_switch = container_labeling_switch_in,
                      container_labeling_tick = container_labeling_tick_in,
                      education_switch = education_switch_in,
                      education_frequency = education_frequency_in,
                      priority_price_over_recycling_vec = priority_price_over_recycling_vec,
                      investing_threshold = 0.5)
    
    share_recycled_plastic = np.zeros(time_span)
    time = np.zeros(time_span)
    municipality_budget = np.zeros(time_span)
    municipality_budget_mean = np.zeros(time_span)
    municipality_budget_median = np.zeros(time_span)
    
    for t in range(time_span):
        model.step()
        share_recycled_plastic[t] = model.total_recycled_plastic/model.total_potential_plastic_waste
        time[t] = t + 1
        for municipality in model.municipalities:
            municipality_budget[t] += municipality.budget_plastic_recycling
        municipality_budget_mean[t] = np.mean(municipality_budget[t])
        municipality_budget_median[t] = np.median(municipality_budget[t])
        
    return {'TIME':time,
            'share_recycled_plastic':share_recycled_plastic,
            'total_municipality_budget':municipality_budget,
            'mean_municipality_budget':municipality_budget_mean,
            'median_municipality_budget':municipality_budget_median}

#%%

ema_model()

#%%

ema_logging.log_to_stderr(ema_logging.INFO)

uncertainties = [IntegerParameter('n_recycling_companies_in', 5, 10),
                 IntegerParameter('funding_municipalities_in', 10, 100),
                 BooleanParameter('improving_tech_recycling_company_in'),
                 IntegerParameter('reverse_collection_tick_in', 0, 239),
                 IntegerParameter('container_labeling_tick_in', 0, 239),
                 IntegerParameter('education_frequency_in', 12, 48),
                 RealParameter('priority_price_over_recycling_mean_in', 0.2, 0.8),
                 RealParameter('investing_threshold', 0.2, 0.8)] 

outcomes = [TimeSeriesOutcome('TIME'),
            TimeSeriesOutcome('share_recycled_plastic'),
            TimeSeriesOutcome('total_municipality_budget'),
            TimeSeriesOutcome('mean_municipality_budget'),
            TimeSeriesOutcome('median_municipality_budget')]

py_model = Model('Python', function = ema_model)
py_model.uncertainties = uncertainties
py_model.outcomes = outcomes

#%% 

n_exp = 10000

with MultiprocessingEvaluator(py_model) as evaluator:
    results_lhs = evaluator.perform_experiments(scenarios = n_exp, uncertainty_sampling = LHS)

exp_lhs, out_lhs = results_lhs

#%%

import statsmodels.api as sm

X = pd.DataFrame(exp_lhs).drop(['model','policy'], inplace = False, axis = 1)
X_0 = sm.add_constant(X)

est = sm.OLS(out_lhs['share_recycled_plastic'][:, -1], X_0.astype(float)).fit()
print(est.summary())
print(est.params)

#%% prim

x = exp_lhs
y = out_lhs['share_recycled_plastic'][:, -1] > 0.5

#%%

prim_alg = prim.Prim(x, y, threshold = 0.8)
box1 = prim_alg.find_box()

box1.show_tradeoff()
plt.show()

#%%

box1.inspect(style = 'graph')
plt.show()

#%%

fs = feature_scoring.get_feature_scores_all(exp_lhs, out_lhs)
sns.heatmap(fs, cmap = 'viridis', annot = True)
plt.show()
