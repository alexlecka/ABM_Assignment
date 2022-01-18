from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import VisualizationElement

from main import ABM_model
from main import defined_municipalities
import numpy as np


#%% Server
### Graphas to be plotted in server
chart_recycling_rate = ChartModule([{'Label': 'Total recycling rate', 'Color': 'Black'},
                                    {'Label': 'Separation rate households', 'Color': 'Blue'},
                                    {'Label': 'Recycling efficiency companies', 'Color': 'Red'}],
                                   data_collector_name = 'datacollector_recycling_rate')

chart_budget_municipalities = ChartModule([{'Label': 'Budget municipalities', 'Color': 'Black'},
                                           {'Label': 'Budget recycling companies', 'Color': 'Red'}],
                                   data_collector_name = 'datacollector_budgets')

class BarchartModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["BarchartModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        return [municipality.budget_plastic_recycling for municipality in model.municipalities]


histogram = BarchartModule(list(range(10)), 200, 500)

model_params = {'defined_municipalities': defined_municipalities,
                'n_recycling_companies': UserSettableParameter("slider",
                                                               "Number of recycling companies",
                                                               value = 10,
                                                               min_value = 3,
                                                               max_value = 100,
                                                               step = 1
                                                               ),
                'funding_municipalities': UserSettableParameter("slider",
                                                               "Yearly funding municipality",
                                                               value = 2000,
                                                               min_value = 100,
                                                               max_value = 50000,
                                                               step = 1
                                                               ),
                'improving_tech_recycling_company': UserSettableParameter('checkbox',
                                                                          'Recycling companies investing into new technologies',
                                                                          value = True),
                'reverse_collection_switch':UserSettableParameter('checkbox',
                                                                  'Policy 1: Reverse collection',
                                                                  value = True),
                'reverse_collection_tick': UserSettableParameter('slider',
                                                                 'Policy 1:Tick of implementation of reverse collection',
                                                                 value = 100,
                                                                 min_value = 0,
                                                                 max_value = 239,
                                                                 step = 1),
                'education_switch': UserSettableParameter('checkbox',
                                                          'Policy 2: Communication and Education',
                                                          value = False),
                'education_forgetting_frequency': UserSettableParameter('slider',
                                                                        'Policy 3: Communication and Education frequency',
                                                                        value= 12,
                                                                        min_value=12,
                                                                        max_value= 100,
                                                                        step= 1),

                'container_labeling_switch': UserSettableParameter('checkbox',
                                                                   'Policy 3: Instructions on plastic bags and containers',
                                                                   value = False),
                'container_labeling_tick': UserSettableParameter('slider',
                                                                 'Policy 3: Tick of implementation of instruction on plastic bags and containers',
                                                                 value = 101,
                                                                 min_value= 0,
                                                                 max_value= 239,
                                                                 step = 1),


                }

server = ModularServer(ABM_model,
                       [chart_recycling_rate, chart_budget_municipalities, histogram],
                       'Some name',
                       model_params)

server.port = 8521
server.launch()