import yaml
import random
import pyrankvote as pyvote
import llm_president_brain
import llm_departments
from lanchester import lanchester_battle
import networkx as nx


class political_party:
    def __init__(self, priorities, popularity, name, country):
        self.priorities = priorities
        self.popularity = popularity
        self.name = name
        self.country = country

    def campaign(self, netpopularity):
        self.popularity = max(self.popularity - netpopularity, 0)

    def apply_metrics(self):
        for key in self.priorities.keys():
            if self.country.Metrics[key] >= self.priorities[key]:
                self.country.Metrics[key] -= self.priorities[key]*(0.1*abs(self.country.Metrics[key]-self.priorities[key]))
            else:
                self.country.Metrics[key] += self.priorities[key]*(0.1*abs(self.country.Metrics[key]-self.priorities[key]))

    def choose_goal(self):
        denominator = 0
        for priority in self.priorities.keys():
            denominator += self.priorities[priority]
        
        largest_priority = None
        largest_priority_percentage = 0
        for priority in self.priorities.keys():
            support = self.priorities[priority]
            if support > largest_priority_percentage:
                largest_priority_percentage = support
                largest_priority = priority
            if random.randrange(0,100)/100 < support/denominator:
                return priority
        
        return largest_priority


class department:
    def __init__(self, name, share_of_power, country):
            self.name = name
            self.share_of_power = share_of_power
            self.country = country
    
    def refuse_command(self):
        print("No.")
        return False

    def demand_action(self, action_demanded, args):
        action_demanded(args)
        return 1 


class war_department(department):
    def choose_action(self, goal):
        campaign_planned = False
        if self.country.at_war:
            target, money_balance, effectiveness = self.plan_campaign()
            if (target, money_balance, effectiveness) == (0, 0, 0):
                self.country.econ_Dep.buy("War Materials", 20)
            else:
                campaign_planned = True
        juiciness = self.country.Treasury
        option = None

        if goal == 'Economic Success':
            for option_name in self.country.Diplomatic_Relationships.keys():
                if self.country.Diplomatic_Relationships[option_name] == "War" and not self.country.framework.countries[option_name].died:
                    new_juice = self.country.framework.countries[option_name].Treasury
                    if new_juice > juiciness:
                        juiciness = new_juice
                        option = option_name
            if juiciness == self.country.Treasury:
                self.country.econ_Dep.check_the_books()
            elif random.random() < 0.4:
                self.raid(option)
        elif goal == 'Dominance':
            if campaign_planned:
                self.attack(target, money_balance, effectiveness)
            else:
                self.country.econ_Dep.buy("War Materials", -20)
        elif goal == 'Happiness':
            self.country.econ_Dep.buy("War Materials", 20)
        else:
            # print('invalid goal')
            return 'invalid goal'

    def plan_campaign(self):
        max_score = 0
        final_target = None
        my_yumminess = self.country.Treasury / self.country.framework.average_treasury
        my_spikiness = self.country.army_ratio * self.country.population / self.country.framework.average_population
        my_score = my_yumminess + my_spikiness
        for nation_name in self.country.Diplomatic_Relationships.keys():
            if self.country.Diplomatic_Relationships[nation_name] == "War":
                target = self.country.framework.countries[nation_name]
                yumminess = target.Treasury / self.country.framework.average_treasury
                spikiness = target.war_knowledge * target.army_ratio * target.population / self.country.framework.average_population
                score = yumminess + spikiness

                if score > max_score:
                    max_score = score
                    final_target = nation_name

        if max_score*1.2 > my_score:
            return 0, 0, 0

        money_comparison = self.country.Treasury - self.country.framework.countries[final_target].Treasury
        combat_effectiveness = self.country.war_knowledge

        return final_target, money_comparison, combat_effectiveness

    def raid(self, target):
        juice = self.country.framework.countries[target].Treasury
        self.country.framework.countries[target].Treasury = juice * 0.9
        self.country.Treasury += juice * 0.1
        self.country.raided_this_tick = True

    def attack(self, target, money_balance, effectiveness):
        self.country.attacked_this_tick = True

        the_ENEMY = self.country.framework.countries[target]

        A = self.country.population * self.country.army_ratio
        B = the_ENEMY.army_ratio
        alpha = self.country.war_knowledge
        beta = the_ENEMY.war_knowledge

        res = lanchester_battle.run_battle(A, alpha, B, beta)

        if res[0] == "A":
            self.country.won_battles += 1
            self.country.population -= res[1]
            the_ENEMY.population -= B
            the_ENEMY.won_battles -= 1
        if res[0] == "B":
            self.country.won_battles -= 1
            self.country.population -= A
            the_ENEMY.population -= res[1]
            the_ENEMY.won_battles += 1
        if res[0] == "Tie":
            self.country.population -= A
            the_ENEMY.population -= B

    def defend(self, target, defenders):
        #print(f'Defended {target} with {defenders}')
        pass
    def wait(self):
        #print(f'Waited')
        pass

class econonmics_department(department):
    def __init__(self, name, share_of_power, country):
        super().__init__(name, share_of_power, country)
        self.tax_percentage = 0.3

    def choose_action(self, goal):
        #check the books before you do anything
        self.check_the_books()

        if goal == "Economic Success":
            choice_1, choice_2, choice_3 = "increase taxes", "increase anti-corruption", "decrease inflation"
            choice = random.choice([choice_1, choice_2, choice_3])
            if choice == 1:
                self.tax_percentage += 0.01
                self.country.Debt -= self.country.Treasury * 0.05
                self.country.Treasure -= self.country.Treasury * 0.05
                self.country.happiness -= 0.01
            elif choice == 2:
                self.country.Corruption -= 0.005
                self.country.happiness += 0.001
            elif choice == 3:
                self.country.inflation -= 0.005
                self.country.happiness += 0.002

        elif goal == "Dominance":
            choice_1, choice_2, choice_3 = "increase the taxable population", "buy war materials", "buy food"
            choice = random.choice([choice_1, choice_2, choice_3])
            if choice == 1:
                self.country.percentage_poor += 0.01
                self.country.happiness -= 0.01
            elif choice == 2:
                self.buy("War Materials", 20)
            elif choice == 3:
                self.buy("Food", 20)
        
        elif goal == "Happiness":
            choice_1, choice_2, choice_3 = "lower taxes", "cut unnecessary anti-corruption measures", "lower interest rates"
            choice = random.choice([choice_1, choice_2, choice_3])
            if choice == 1:
                self.tax_percentage -= 0.01
                self.country.happiness += 0.01
            elif choice == 2:
                self.country.Corruption += 0.005
                self.country.Treasury += self.country.Treasury * 0.05
                self.country.happiness += 0.002
            elif choice == 3:
                self.country.inflation += 0.005
                self.take_loan(self.country.Treasury * 0.05)
                self.country.happiness += 0.005
        
    def check_the_books(self):
        #income
        tax_income = (self.country.population) * self.country.percentage_poor * self.tax_percentage * (1-self.country.Corruption) * self.country.econonmics_knowledge
        income = tax_income * self.country.happiness
        #expenses
        interest_payments = self.country.Debt * 0.05
        army_upkeep = self.country.Geographic_Resources["War Materials"] * 0.5
        food_expenses = self.country.population * 0.05
        
        #inflation
        self.country.Treasury = self.country.Treasury * (1-self.country.inflation)

        #print(interest_payments)
        #print(army_upkeep)
        #print(food_expenses)

        expenses = interest_payments + army_upkeep + food_expenses

        balance = int(income - expenses) + 5000

        self.country.Treasury += balance
        self.country.balance_this_tick = balance
        #print(f"Balance of {balance}, income of {income} minus expenses of {expenses}")

    def tax_the_poor(self, percent):
       self.tax_percentage = percent
       # print(f'Taxed the poor by {percent} percent')

    def take_loan(self, amount):
        self.country.Treasury += amount
        self.country.Debt += amount
        #print(f'Took a loan of size {amount}')

    def buy(self, product, amount):
        self.country.Geographic_Resources[product] += amount
        self.country.Treasury -= amount * 100
        #print(f'Bought {amount} of {product}')

class peace_department(department):
    def choose_action(self, goal):
        options = []
        for option_name in self.country.Diplomatic_Relationships.keys():
            self.country.countries_known = len(self.country.Diplomatic_Relationships.keys())
            if self.country.Diplomatic_Relationships[option_name] == "War":
                options.append(option_name)

        self.country.num_enemies = len(options)

        if goal == 'Economic Success':
            pass
        elif goal == 'Dominance':
            if random.randint(1,2) == 1:
                if options == []:
                    #print("Declared War")
                    option = random.choice(list(self.country.Diplomatic_Relationships.keys()))
                    self.country.framework.G.add_edge(option, self.country.Name, relationship="War")
                    self.declare_war(option)
                    self.country.bought_war_materials = True
                    self.country.econ_Dep.buy("War Materials", 50)
            else:
                if options != []:
                    option = random.choice(options)
                    self.country.framework.G.add_edge(option, self.country.Name, relationship="Peace")
                    offer = 'eternal love and affection'
                    self.request_relationship(option, offer)
        elif goal == 'Happiness':
            if options != []:
                offer = 'eternal submission'
                target = random.choice(options)
                self.offer_peace(target, offer) 
            else:
                self.country.econ_Dep.buy("Food", 1)
        else:
            #print('invalid goal')
            return 'invalid goal'
        
    def declare_war(self, target):
        self.country.Diplomatic_Relationships[target] = "War"
        self.country.framework.countries[target].Diplomatic_Relationships[self.country.Name] = "War"
        #print(f'Declared war on {target}')
    def offer_peace(self, target, offer):
        self.country.Diplomatic_Relationships[target] = "Peace"
        self.country.framework.countries[target].Diplomatic_Relationships[self.country.Name] = "Peace"
        #print(f'Made peace with {target} with the terms of {offer}')
    def request_relationship(self, target, offer):
        #print(f'Requested {offer} relationship with {target}')
        pass
    def process_relationship_request(self, target, offer):
        #print(f'Processed {offer} offer from {target}')
        pass

class research_department(department):
    def choose_action(self, goal):
        if goal == 'Economic Success':
            self.research_economics()
        elif goal == 'Dominance':
            if random.randint(1,2) == 1:
                self.reseach_war()
            else:
                self.research_peace()
        elif goal == 'Happiness':
            self.research_research()
        else:
            print('invalid goal')
            return 'invalid goal'
        
    def research_research(self):
        self.country.research_knowledge += 0.005 * self.country.research_knowledge
        #print('Reseached research')
    def research_economics(self):
        self.country.econonmics_knowledge += 0.01 * self.country.research_knowledge
        #print('Reseached economics')
    def reseach_war(self):
        self.country.war_knowledge += 0.01 * self.country.research_knowledge
        #print('Reseached war')
    def research_peace(self):
        self.country.peace_knowledge += 0.01 * self.country.research_knowledge
        #print('Reseached peace')

class country:
    def __init__(self, Name, GDP, Culture, Treasury, Debt, Net_Cash_Flow, Diplomatic_Relationships, Geographic_Resources, Public_Sentiment, Corruption, Metric_Priority, population, percentage_poor, brain_type, framework):
        self.brain_type = brain_type
        self.Name = Name
        self.GDP = GDP
        self.Culture = Culture 
        self.Treasury = int(Treasury)
        self.Debt = int(Debt) 
        self.Net_Cash_Flow = float(Net_Cash_Flow)
        self.Diplomatic_Relationships = Diplomatic_Relationships 
        self.Geographic_Resources = Geographic_Resources 
        self.Public_Sentiment = Public_Sentiment 
        self.Corruption = Corruption
        self.Metric_Priority = Metric_Priority
        self.Metrics = {'Dominance':0, 'Economic Success':0, 'Happiness':0}
        self.ruling_party = None
        self.econonmics_knowledge = 1
        self.war_knowledge = 1
        self.peace_knowledge = 1
        self.research_knowledge = 1
        self.population = population
        self.army_ratio = 0.1
        self.percentage_poor = percentage_poor - self.army_ratio
        self.framework = framework
        self.ruling_party = None
        self.attacked_this_tick = False
        self.raided_this_tick = False
        self.balance_this_tick = 0
        self.bought_war_materials = False
        self.countries_known = len(self.Diplomatic_Relationships.keys())
        self.num_enemies = 0
        self.inflation = 0.02
        self.happiness = 1
        self.at_war = self.is_at_war()
        self.won_battles = 0

        self.econ_picks = 0
        self.dom_picks = 0
        self.happy_picks = 0

        if self.brain_type == 'base':
            self.war_Dep = war_department(self, 0.4, self)
            self.peace_Dep = peace_department("Peace Department", 0.1, self)
            self.econ_Dep = econonmics_department("Economics Department", 0.3, self)
            self.research_Dep = research_department("Research Department", 0.2, self)
        else:
            self.war_Dep = war_department(self, 0.4, self)
            self.peace_Dep = peace_department("Peace Department", 0.1, self)
            self.econ_Dep = llm_departments.econonmics_department("Economics Department", 0.3, self)
            self.research_Dep = research_department("Research Department", 0.2, self)
        
        self.carrying_capacity = self.Geographic_Resources['Food']*500

        self.departments_list = [self.war_Dep, self.peace_Dep, self.econ_Dep, self.research_Dep]
        
        self.hippies = political_party({'Dominance':0.2, 'Economic Success':0.6, 'Happiness':1}, 0.5, 'hippies', self)
        self.screaming_ball_of_rage = political_party({'Dominance':1, 'Economic Success':0.4, 'Happiness':0.2}, 0.1, 'screaming_ball_of_rage', self)

        self.parties = [self.hippies, self.screaming_ball_of_rage]

        self.winner = False
        self.died = False
        

    def give_command(self, department, command):
        #give commands to department
        pass

    def is_at_war(self):
        for nation_name in self.Diplomatic_Relationships.keys():
            if self.Diplomatic_Relationships[nation_name] == "War":
                return True
                #print("We are at war!")
        return False

    def run_election(self):
        
    #     voting_population = 0.1 * self.population
    #     candidates = []
    #     for i in self.parties:
    #         candidates.append(pyvote.Candidate(i.name))

    #     ballots = []

    #     for i in range(int(voting_population)):
    #         random.shuffle(candidates)
    #         ballots.append(pyvote.Ballot(ranked_candidates=candidates))

    #     election_result = pyvote.instant_runoff_voting(candidates, ballots)

    #    # random.choice()
        
    #     results = election_result.get_winners()[0]

    #     for i in self.parties:
    #         if i.name == results.name:
    #             self.ruling_party = i
    #             i.popularity = results.number_of_votes  

        #changing_party = random.choice(self.parties)
        for p in self.parties:
            p.campaign((random.random()-0.5)/4)
        
        ruling_party = None 
        ruling_popularity = 0
        for party in self.parties:
            if party.popularity > ruling_popularity:
                 ruling_popularity = party.popularity
                 ruling_party = party
        if ruling_party == None:
            ruling_party = self.ruling_party

        self.ruling_party = ruling_party
        #print(f"Balance of power, hippies vs screaming ball of rage: {self.parties[0].popularity} vs {self.parties[1].popularity}")
        #print(f"Ruling party is {self.ruling_party.name} with popularity of {self.ruling_party.popularity}")
        #print(f'Their metrics are {self.ruling_party.priorities}')
        self.ruling_party.apply_metrics()

    def choose_actions(self):
        self.attacked_this_tick = False
        self.raided_this_tick = False
        self.bought_war_materials = False
        self.carrying_capacity = self.Geographic_Resources["Food"]*500
        self.at_war = self.is_at_war()
        initial_pop = self.population
        growth_rate = 0.02
        if initial_pop != 0 and self.carrying_capacity != 0:
            self.population += growth_rate * initial_pop * (1 - initial_pop/self.carrying_capacity)
        
        if initial_pop == 0 or self.carrying_capacity == 0:
            self.framework.kill_country(self.Name)
            print("HOW")


            return
        
        #print(f"|--------------------------{self.Name} Turn--------------------------|")
        if self.brain_type == "base":
            self.run_election()
            goal_for_term = self.ruling_party.choose_goal()
            #print(goal_for_term + "<----- NOT OFF")
        elif self.brain_type == "llm_president":
            party = "Balancers"
            views = "pragmatism and balanced policies.  You will try to choose objectives that haven't been picked as often"

            if self.population >= self.framework.average_population + 0.2 * self.framework.average_population:
                population_level = "high"
            elif self.population <= self.framework.average_population - 0.2 * self.framework.average_population:
                population_level = "low"
            else:
                population_level = "medium"
                
            aggression_level = str(self.Metric_Priority['Dominance'])

            if self.balance_this_tick >= self.framework.average_income + 0.2 * self.framework.average_income:
                income_level = "high"
            elif self.balance_this_tick <= self.framework.average_income - 0.2 * self.framework.average_income:
                income_level = "low"
            else:
                income_level = "medium"

            if self.Geographic_Resources['Food'] >= self.framework.average_food + 0.2 * self.framework.average_food:
                food_level = "high"
            elif self.Geographic_Resources['Food'] <= self.framework.average_food - 0.2 * self.framework.average_food:
                food_level = "low"
            else:
                food_level = "medium"

            if self.Geographic_Resources['War Materials'] >= self.framework.average_wm + 0.2 * self.framework.average_wm:
                wm_level = "high"
            elif self.Geographic_Resources['War Materials'] <= self.framework.average_wm - 0.2 * self.framework.average_wm:
                wm_level = "low"
            else:
                wm_level = "medium"

            num_enemies = self.num_enemies
            
            num_dom = self.dom_picks
            num_hap = self.happy_picks
            num_econ = self.econ_picks

            llm_brain = llm_president_brain.llm_president_brain()

            llm_goal_for_term = llm_brain.priority(party, views, population_level, aggression_level, income_level, food_level, wm_level, num_enemies, num_dom, num_hap, num_econ)

            #print(llm_goal_for_term + "<----- OOF")

            if "Happiness" in llm_goal_for_term:
                goal_for_term = "Happiness"
            if "Dominance" in llm_goal_for_term:
                goal_for_term = "Dominance"
            if "Economic" in llm_goal_for_term:
                goal_for_term = "Economic Success"
            
        self.priority_this_tick = goal_for_term

        #print(f"The goal for the term is {goal_for_term}")

        if goal_for_term == "Happiness":
            self.happy_picks += 1
        elif goal_for_term == "Dominance":
            self.dom_picks += 1
        elif goal_for_term == "Economic Success":
            self.econ_picks += 1

        if self.balance_this_tick > 0:
            balance = "positive"
        elif self.balance_this_tick < 0:
            balance = "negative"
        else:
            balance = "balanced"

        for dep in self.departments_list:
            if type(dep) == llm_departments.econonmics_department:
                dep.choose_action(balance, goal_for_term, population_level, income_level, food_level, wm_level, num_enemies)
            else:
                dep.choose_action(goal_for_term)
        #print(f"|--------------------------End of {self.Name} turn--------------------------|\n")

    def tick(self):
        #print(f"|--------------  {self.Name} Turn  --------------|")
        self.choose_actions()

    def display(self):
        print(
            f"Name = {self.Name}\n",
            f"GDP = {self.GDP}\n",
            f"Culture = {self.Culture}\n", 
            f"Treasury = {self.Treasury}\n", 
            f"Debt = {self.Debt}\n", 
            f"Net Cash Flow = {self.Net_Cash_Flow}\n", 
            f"Diplomatic Relationships = {self.Diplomatic_Relationships}\n",
            f"Geographic Resources = {self.Geographic_Resources}\n",
            f"Public Sentiment = {self.Public_Sentiment}\n",
            f"Corruption = {self.Corruption}\n",
            f"Metric Priority= {self.Metric_Priority}\n",
            f"Economics Knowledge = {self.econonmics_knowledge}\n",
            f"War Knowledge = {self.war_knowledge}\n",
            f"Peace Knowledge = {self.peace_knowledge}\n",
            f"Research Knowledge = {self.research_knowledge}\n"
        )

class simulation_bed:
    def __init__(self, country_data=[], population_data=None, geographic_data=None):
        self.population_data = population_data
        self.geographic_data = geographic_data        
        self.country_list = country_data
        self.countries = dict()
        self.all_attributes_over_time = []
        self.dead_countries = dict()
        self.average_population = 0
        self.average_income = 0
        self.average_food = 0
        self.average_wm = 0
        self.average_treasury = 0
        self.G = nx.complete_graph([country(*c, self).Name for c in self.country_list])
        for c in self.country_list:
            self.countries[c[0]] = country(*c, self)
        
    def set_avg_pop(self):
        pop = 0
        bap = 0
        for c_name in self.countries.keys():
            bap+=1
            pop += self.countries[c_name].population
        self.average_population = pop//bap

    def set_avg_inc(self):
        pop = 0
        bap = 0
        for c_name in self.countries.keys():
            bap+=1
            pop += self.countries[c_name].balance_this_tick
        self.average_income = pop//bap

    def set_avg_food(self):
        food = 0
        bap = 0
        for c_name in self.countries.keys():
            bap+=1
            food += self.countries[c_name].Geographic_Resources['Food']
        self.average_food = food//bap

    def set_avg_wm(self):
        wm = 0
        bap = 0
        for c_name in self.countries.keys():
            bap+=1
            wm += self.countries[c_name].Geographic_Resources['War Materials']
        self.average_treasury = wm//bap

    def set_avg_treasury(self):
        t = 0
        bap = 0
        for c_name in self.countries.keys():
            bap+=1
            t += self.countries[c_name].Treasury
        self.average_wm = t//bap

    def tick(self):
        self.set_avg_pop()
        self.set_avg_inc()
        self.set_avg_food()
        self.set_avg_wm()
        self.set_avg_treasury()

        attributes = dict()
        for c in self.countries.keys():
            if self.countries[c].population <= 0 and not self.countries[c].died:
                self.kill_country(c, "population")

            if self.countries[c].carrying_capacity <= 100 and not self.countries[c].died:
                self.kill_country(c, "carrying_capacity")
            
            if self.countries[c].Treasury <= 0 and not self.countries[c].died:
                self.kill_country(c, "money")

            if self.countries[c].died:
                attributes[c] = {"Treasury":0, 
                                  "Population":0, 
                                  "Debt":0,
                                  "Economics Knowledge":0, 
                                  "War Knowledge":0, 
                                  "Peace Knowledge":0, 
                                  "Research Knowledge":0,
                                  "Attacks":0,
                                  "Food":0,
                                  "War Materials":0,
                                  "Raids":0,
                                  "Balance":0,
                                  "Bought War Materials":0,
                                  "Number of Enemies":0,
                                  "Death":self.countries[c].died,
                                  "Economic Picks":0,
                                  "Dominance Picks":0,
                                  "Happiness Picks":0,
                                  "Happiness": 0,
                                  "Won Battes": 0}
                continue

            self.countries[c].tick()
            curr_country = self.countries[c]
            attributes[curr_country.Name] = {"Treasury":curr_country.Treasury, 
                                  "Population":curr_country.population, 
                                  "Debt":curr_country.Debt,
                                  "Economics Knowledge":curr_country.econonmics_knowledge, 
                                  "War Knowledge":curr_country.war_knowledge, 
                                  "Peace Knowledge":curr_country.peace_knowledge, 
                                  "Research Knowledge":curr_country.research_knowledge,
                                  "Attacks":curr_country.attacked_this_tick,
                                  "Food":curr_country.Geographic_Resources["Food"],
                                  "War Materials":curr_country.Geographic_Resources["War Materials"],
                                  "Raids":curr_country.raided_this_tick,
                                  "Balance":curr_country.balance_this_tick,
                                  "Bought War Materials":curr_country.bought_war_materials,
                                  "Number of Enemies":curr_country.num_enemies,
                                  "Death":curr_country.died,
                                  "Economic Picks":curr_country.econ_picks,
                                  "Dominance Picks":curr_country.dom_picks,
                                  "Happiness Picks":curr_country.happy_picks,
                                  "Happiness":curr_country.happiness,
                                  "Won Battes": curr_country.won_battles}
        
        return attributes
    
    def deathmatch(self):
        boo = False        
        i = 0
        while not boo and i <= 100:
            print(f"TIME {i}")
            some = self.tick()
            some["timestamp"] = str(i)
            self.all_attributes_over_time.append(some)
            alive = 0
            for c_name in self.countries.keys():
                if not self.countries[c_name].died:
                    alive += 1
            if alive == 1:
                boo = True
            i += 1

        return self.all_attributes_over_time

    def run(self, number_of_ticks):
        for i in range(number_of_ticks):
            print(f"TICK {i}")
            some = self.tick()
            some["timestamp"] = str(i)
            self.all_attributes_over_time.append(some)
        
        self.print_graph()
        return self.all_attributes_over_time

    def list_countries(self):
        for c in self.countries.keys():
            print(self.countries[c].Name)

    def print_detailed_country_list(self):
        for c in self.countries.keys():
            self.countries[c].display()


    def process_map(self, a_map, map_type):
        if map_type == "geomap":
            self.__process_geo_map(a_map)
        
        pass

    def process_planning(self, yaml_plan):
        #print(os.listdir())
        with open(yaml_plan, "r") as stream:
            try:
                print(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

    def add_country(self, country_data):
        self.countries[country_data[0]] = country(*country_data, self)
        self.G.add_node(self.countries[country_data[0]].Name)


        for country_name in self.countries.keys():
            if len(self.countries.keys()) > len(self.countries[country_name].Diplomatic_Relationships):
                for c_key in self.countries.keys():
                    if c_key != country_name:
                        if c_key not in self.countries[country_name].Diplomatic_Relationships.keys():
                            self.countries[country_name].Culture[c_key] = (0, "ambivalent")
                            self.countries[c_key].Culture[country_name] = (0, "ambivalent")

                            self.G.add_edge(country_name, c_key, relationship="Peace")

                            self.countries[country_name].Diplomatic_Relationships[c_key] = (f"Peace")
                            self.countries[c_key].Diplomatic_Relationships[country_name] = (f"Peace")

        

        

    def kill_country(self, c, reason):
        self.dead_countries[c] = self.countries[c]
        self.countries[c].died = True
        print(f"{c} got BTFO'd due to {reason}")

    def print_graph(self):
        nx.write_graphml(self.G, "most_recent.graphml")
                
