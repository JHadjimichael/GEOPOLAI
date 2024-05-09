import requests
from meta_ai_api import MetaAI
class llm_president_brain():
    

    def __init__(self):
        
        pass

    def priority(party, views, population_level, aggression_level, income_level, food_level, wm_level, num_enemies, num_dom, num_hap, num_econ):
        string = f"You are the elected president of a nation as a member of the {party} Party, which holds the policy position of {views}. In this world, nations are defined by three key attributes: Their population, their aggression, and their income.  Your population is {population_level}, your aggression is {aggression_level} out of 1, and your income is {income_level}. Your food level, which determines your population carrying capacity, is currently {food_level}.  Your war material supplies, which are needed to attack enemies, are {wm_level}.  You are at war with {num_enemies} other nations. Your main objective for your term in one word is between 'Dominance' (directs your nation to attack others, lose population and income, but weaken enemies), 'Economic Success' (make more money), and 'Happiness' (make peace with enemies and increase the population).  Of these you've chosen Dominance {num_dom} times, Happiness {num_hap} times, and Economic Success {num_econ} times.  Your choice between the three, using all that information and without punctuation, is therefore:"
        #print(string)

        res = MetaAI().prompt(message=string)
        #print(res)
        return res['message'].split('\n')[0]

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

        print(res_str)
        return res_str.split(' ')[0]

#print("choosing national policy")
#print(llm_president_brain.priority("Schemers", "average machiavellian", "medium", "medium", "medium", "medium", "medium", "0", "0", "0", "0"))