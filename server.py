from mesa.visualization.ModularVisualization import VisualizationElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from main import defined_municipalities
from main import ABM_model

#%% server

# graphas to be plotted in server
chart_recycling_rate = ChartModule([{'Label':'Total recycling rate', 'Color': 'Black'},
                                    {'Label':'Separation rate households', 'Color': 'Blue'},
                                    {'Label':'Recycling efficiency companies', 'Color': 'Red'}],
                                   data_collector_name = 'datacollector_recycling_rate')

chart_budget_municipalities = ChartModule([{'Label':'Budget municipalities', 'Color': 'Black'},
                                           {'Label':'Budget recycling companies', 'Color': 'Red'}],
                                   data_collector_name = 'datacollector_budgets')

chart_budget_single_munacipalities = ChartModule([{'Label': 'M1 recycling budget', 'Color': '#C84C31'},
                                                  {'Label': 'M2 recycling budget', 'Color': '#98C831'},
                                                  {'Label': 'M3 recycling budget', 'Color': '#C431C8'},
                                                  {'Label': 'M4 recycling budget', 'Color': '#8231C8'},
                                                  {'Label': 'M5 recycling budget', 'Color': '#5779CC'},
                                                  {'Label': 'M6 recycling budget', 'Color': '#57CBCC'},
                                                  {'Label': 'M7 recycling budget', 'Color': '#16E945'},
                                                  {'Label': 'M8 recycling budget', 'Color': '#E9E516'},
                                                  {'Label': 'M9 recycling budget', 'Color': '#E95316'},
                                                  {'Label': 'M10 recycling budget', 'Color': 'Black'}],
                                                 canvas_height = 300,
                                                 data_collector_name= 'datacollector_budget_municipality')

chart_budget_single_recycling_company = ChartModule([{'Label': 'R1 budget', 'Color': '#C84C31'},
                                                      {'Label': 'R2 budget', 'Color': '#98C831'},
                                                      {'Label': 'R3 budget', 'Color': '#C431C8'},
                                                      {'Label': 'R4 budget', 'Color': '#8231C8'},
                                                      {'Label': 'R5 budget', 'Color': '#5779CC'},
                                                      {'Label': 'R6 budget', 'Color': '#57CBCC'},
                                                      {'Label': 'R7 budget', 'Color': '#16E945'},
                                                      {'Label': 'R8 budget', 'Color': '#E9E516'},
                                                      {'Label': 'R9 budget', 'Color': '#E95316'},
                                                      {'Label': 'R10 budget', 'Color': 'Black'}],
                                                     canvas_height = 300,
                                                     data_collector_name= 'datacollector_budget_recycling_companies')


model_params = {'defined_municipalities': defined_municipalities,
                'n_recycling_companies': UserSettableParameter("slider",
                                                               "Number of recycling companies",
                                                               value = 10,
                                                               min_value = 4,
                                                               max_value = 10,
                                                               step = 1
                                                               ),
                'funding_municipalities': UserSettableParameter("slider",
                                                               "Yearly funding municipality (per household)",
                                                               value = 200,
                                                               min_value = 0,
                                                               max_value = 1000,
                                                               step = 1),

                'improving_tech_recycling_company': UserSettableParameter('checkbox',
                                                                          'Investment into new technology (recycling company)',
                                                                          value = False),
                'investing_threshold': UserSettableParameter('slider',
                                                                'Probability of company to invest in new technology',
                                                                value = 0.5,
                                                                min_value= 0,
                                                                max_value= 1,
                                                                step= 0.1),
                'reverse_collection_switch':UserSettableParameter('checkbox',
                                                                  'Policy 1: Reverse waste collection',
                                                                  value = False),
                'reverse_collection_tick': UserSettableParameter('slider',
                                                                 'Time step of implementation of Policy 1',
                                                                 value = 100,
                                                                 min_value = 0,
                                                                 max_value = 239,
                                                                 step = 1),
                'education_switch': UserSettableParameter('checkbox',
                                                          'Policy 2: Communication and education',
                                                          value = False),
                'education_frequency': UserSettableParameter('slider',
                                                                        'Frequency of implementation of Policy 3',
                                                                        value = 12,
                                                                        min_value = 12,
                                                                        max_value = 48,
                                                                        step = 1),
                'container_labeling_switch': UserSettableParameter('checkbox',
                                                                   'Policy 3: Container labeling',
                                                                   value = False),
                'container_labeling_tick': UserSettableParameter('slider',
                                                                 'Time step of implementation of Policy 3',
                                                                 value = 101,
                                                                 min_value = 0,
                                                                 max_value = 239,
                                                                 step = 1)}

server = ModularServer(ABM_model,
                       [chart_recycling_rate, chart_budget_municipalities, chart_budget_single_munacipalities,
                        chart_budget_single_recycling_company],
                       'Alphambos',
                       model_params)

server.port = 8521
server.launch()