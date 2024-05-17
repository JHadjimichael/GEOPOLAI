import random
import llm_department_brain

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
            options = []
            for option_name in self.country.Diplomatic_Relationships.keys():
                if self.country.Diplomatic_Relationships[option_name] == "War" and not self.country.framework.countries[option_name].died:
                    options.append(option_name)
            #print(options)
            
            if random.random() < (0.3 * self.country.war_knowledge) and self.country.Geographic_Resources["War Materials"] > 200 and options != []:
                target = random.choice(options)
                wm = self.country.Geographic_Resources["War Materials"] * 0.3
                f = self.country.Geographic_Resources["Food"] * 0.1
                warmoney = self.country.Treasury * 0.1
                war_chest = max(min(wm, f, warmoney), 0)
                attackers = war_chest
                self.country.Geographic_Resources["War Materials"] = wm-war_chest
                #self.country.Geographic_Resources["Food"] = f-war_chest
                self.country.Treasury -= war_chest
                self.attack(target, attackers)
                self.country.attacked_this_tick = True
            else:
               # print('grrr...')
                pass
        elif goal == 'Happiness':
            self.country.econ_Dep.buy("War Materials", 20)
        else:
           # print('invalid goal')
            return 'invalid goal'

    def raid(self, target):
        juice = self.country.framework.countries[target].Treasury
        self.country.framework.countries[target].Treasury = juice * 0.9
        self.country.Treasury += juice * 0.1
        self.country.raided_this_tick = True

    def attack(self, target, attackers):
        self.country.framework.countries[target].Treasury -= attackers * 5 * 1000 * self.country.war_knowledge
        self.country.framework.countries[target].Geographic_Resources["War Materials"] = self.country.framework.countries[target].Geographic_Resources["War Materials"] - attackers * 1.5 * 10 * self.country.war_knowledge
        self.country.framework.countries[target].Geographic_Resources["Food"] = self.country.framework.countries[target].Geographic_Resources["Food"] - attackers * 1.5
        self.country.framework.countries[target].population -= attackers * 1.5 * 50 * self.country.war_knowledge
        #print(f'Attecked {target} with war chest of {attackers}')
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
