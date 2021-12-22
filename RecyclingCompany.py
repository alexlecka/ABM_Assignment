import random
from mesa import Agent

debugging = False
def debug_print(string):
    if debugging:
        print(string)

# %% Recycling company class

# we want technologies that improve the efficiency of recycling plastics, for
# simplifiation any extra technology improves efficiency and there is no overlap for now

class RecyclingCompany(Agent):
    def __init__(self, unique_id, model, init_money=1000, init_efficiency=0.4, price=50):
        super().__init__(unique_id, model)
        #        self.budget = random.randrange(init_money) #0-1000
        self.id = unique_id
        self.budget = init_money
        self.efficiency = init_efficiency
        self.price = random.randrange(price)
        self.bought_tech = []
        tech_1 = (0.15, 150, 400)
        tech_2 = (0.06, 100, 250)
        tech_3 = (0.03, 70, 150)
        self.all_tech = tech_1, tech_2, tech_3
        self.contract = []

    def provide_offer(self, offer_request):
        for municipality in offer_request:
            municipality.received_offers.append([self, self.efficiency, self.price])
            debug_print('providing offers')

    def new_tech(self):
        random_gen = random.uniform(0, 1)
        for i in range(len(self.all_tech)):
            n = len(self.all_tech)

            if self.budget > self.all_tech[i][2]:  # and self.efficiency < self.model.market_analysis:
                if random_gen > i / (n * 10) and random_gen < (i + 1) / (n * 10):
                    self.bought_tech.append(self.all_tech[i])
                    self.efficiency += self.all_tech[i][0]
                    self.price += self.all_tech[i][1]
                    self.budget = self.budget - self.all_tech[i][2]
                    self.all_tech = self.all_tech[:i] + self.all_tech[i + 1:]

                    break

    def step(self):
        self.new_tech()

    def __str__(self):
        return 'Recycling Company id: {}'.format(self.id)

# class Model(Model):
#    """A model with some number of agents."""
#    def __init__(self, N):
#        self.num_recycling_companies = N
#        self.schedule = RandomActivation(self)

# Create agents
#       for i in range(self.num_recycling_companies):
#            a = RecyclingCompany(i, self)
#            self.schedule.add(a)
#        self.datacollector = DataCollector(
#        agent_reporters={"Budget": "budget",
#                         "Efficiency": "efficiency"})

#    def market_analysis(self):
#        company_efficiencies = [agent.efficiency for agent in self.schedule.agents]
#        x = np.mean(company_efficiencies)
#        return x

#    def step(self):
#        '''Advance the model by one step.'''
#        self.datacollector.collect(self)
#       self.schedule.step()

# model = Model(10)
# for i in range(50):
#    model.step()

# company_budget = [a.budget for a in model.schedule.agents]
# company_efficiency = [a.efficiency for a in model.schedule.agents]
# plt.hist(company_budget)
# plt.show()


# progression= model.datacollector.get_agent_vars_dataframe()


# fig, ax = plt.subplots(1, figsize = (10, 8))
# for i in range(10):
#    agent_budget = progression.xs(i, level="AgentID")
#    agent_budget.Budget.plot()

# fig, ax = plt.subplots(1, figsize = (10, 8))
# for i in range(10):
#   agent_budget = progression.xs(i, level="AgentID")
#  agent_budget.Efficiency.plot()