import replicate
import os

os.environ["REPLICATE_API_TOKEN"] = 'r8_UCRfZiCSktUC84uV7wdt1mPEqDu2zS64HIAAm'


for event in replicate.stream(
    "meta/meta-llama-3-70b-instruct",
    input={
        "top_k": 50,
        "top_p": 0.9,
        "prompt": "Work through this problem step by step:\n\nQ: Sarah has 7 llamas. Her friend gives her 3 more trucks of llamas. Each truck has 5 llamas. How many llamas does Sarah have in total?",
        "max_tokens": 512,
        "min_tokens": 0,
        "temperature": 0.6,
        "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "presence_penalty": 1.15,
        "frequency_penalty": 0.2
    },
):
    print(str(event), end="")