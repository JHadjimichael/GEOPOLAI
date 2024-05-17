import random
import llm_department_brain
from lanchester import lanchester_battle

class llm_department:
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
    
class war_department(llm_department):
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


class econonmics_department(llm_department):
    def __init__(self, name, share_of_power, country):
        super().__init__(name, share_of_power, country)
        self.tax_percentage = 0.3

    def choose_action(self, balance, goal, population_level, income_level, food_level, wm_level, num_enemies):
        #check the books before you do anything
        self.check_the_books()

        if goal == "Economic Success":
            choice_1, choice_2, choice_3 = "gently raise taxes", "increase anti-corruption", "cool inflation"
            choice = llm_department_brain.llm_econ_department_brain.priority(balance, population_level, income_level, food_level, wm_level, num_enemies, choice_1, choice_2, choice_3)
            if "1" in choice:
                choice = 1
            elif "2" in choice:
                choice = 2
            elif "3" in choice:
                choice = 3

            print(choice)

            if choice == 1:
                self.tax_percentage += 0.01
                self.country.Debt -= self.country.Treasury * 0.05
                self.country.Treasury -= self.country.Treasury * 0.05
                self.country.happiness -= 0.01
            elif choice == 2:
                self.country.Corruption -= 0.005
                self.country.happiness += 0.001
            elif choice == 3:
                self.country.inflation -= 0.005
                self.country.happiness += 0.002

        elif goal == "Dominance":
            choice_1, choice_2, choice_3 = "increase the taxable population", "buy war materials", "buy food"
            choice = llm_department_brain.llm_econ_department_brain.priority(balance, population_level, income_level, food_level, wm_level, num_enemies, choice_1, choice_2, choice_3)
            if "1" in choice:
                choice = 1
            elif "2" in choice:
                choice = 2
            elif "3" in choice:
                choice = 3

            print(choice)

            if choice == 1:
                self.country.percentage_poor += 0.01
                self.country.happiness -= 0.01
            elif choice == 2:
                self.buy("War Materials", 20)
            elif choice == 3:
                self.buy("Food", 20)
        
        elif goal == "Happiness":
            choice_1, choice_2, choice_3 = "harshly cut taxes", "decrease anti-corruption measures", "let inflation increase"
            choice = llm_department_brain.llm_econ_department_brain.priority(balance, population_level, income_level, food_level, wm_level, num_enemies, choice_1, choice_2, choice_3)
            if "1" in choice:
                choice = 1
            elif "2" in choice:
                choice = 2
            elif "3" in choice:
                choice = 3
            print(choice)

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

        #print(goal, choice)
            
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

class peace_department(llm_department):
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
                    option = random.choice(list(self.country.Diplomatic_Relationships.keys()))
                    self.declare_war(option)
                    self.country.bought_war_materials = True
                    self.country.econ_Dep.buy("War Materials", 50)
            else:
                if options != []:
                    option = random.choice(options)
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

class research_department(llm_department):
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
