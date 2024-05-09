import requests
from meta_ai_api import MetaAI
class llm_econ_department_brain():
    def __init__(self):
        pass

    def priority(balance, population_level, income_level, food_level, wm_level, num_enemies, choice_1, choice_2, choice_3):
        department_description = f"You are the department head of the economic department of our great nation. You act as an extention of our far-sighted president. The president has much more information about the state of the world and the country.  The president is trust\n"
        give_choices = f"You will be picking an action for your department to take.  Your *only* choices, as mandated by the president, are between option 1: {choice_1}, option 2: {choice_2}, or option 3: {choice_3}.\n"
        current_state_intro = f"The state of our nation as compared to our neighbors is as follows:\n"
        income = f"\t- Tax income: {income_level}\n"
        pop = f"\t- Population Level: {population_level}\n"
        food = f"\t- Food (determines population carrying capacity) Level: {food_level}\n"
        wm = f"\t- War Materials (determines attack strength) Level: {wm_level}\n"
        enemies = f"Additionally, our nation is currently at war with the following number of countries: {num_enemies}\n"
        balance = f"Finally, our balance, or our current income minus expenses, is currently {balance}"
        outro = f"That is all the information currently available. Using your expertise, and only stating either '1', '2', or '3', the option you would pick if you had to would be:"

        message = department_description + give_choices + current_state_intro + income + pop + food + wm + enemies + outro
        print(message)
        res = MetaAI().prompt(message=message)
        print(res)
        return res['message'].split('\n')[0] 

class llm_department_brain():
    def __init__(self):
        pass

    def priority(department, party, views, population_level, aggression_level, income_level, food_level, wm_level, num_enemies, num_dom, num_hap, num_econ):
        string = f"You are the department head of the {department} of our great nation"
        string = f""
        #print(string)
        sys_prompt = f"""systemPrompt:{string}"""
        
        ret = {
            "prompt":sys_prompt,
            "temperature":0.75,
            "topP":0.9,
            "maxTokens": 600
        }
        res_str = ""
        response = requests.post('https://fumes-api.onrender.com/llama3',
        json=ret, stream=True)
        for chunk in response.iter_content(chunk_size=1024):  
            if chunk:
                res_str += chunk.decode('utf-8')

        return res_str.split(' ')[0]

#print("choosing econ policy")
#print(llm_econ_department_brain.priority("low", "high", "low", "low", "high", 0, "decreasing inflation", "fight corruption", "raise taxes"))