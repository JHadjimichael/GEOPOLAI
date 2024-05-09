from groq import Groq

client = Groq(
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)
