import openai

# Replace with your OpenAI API key
openai.api_key = "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"

try:
    response = openai.Embedding.create(
        input=["Test embedding generation"],
        engine="text-embedding-ada-002"
    )
    print("Embedding generated successfully:", response['data'][0]['embedding'])
except openai.error.OpenAIError as e:
    print("Error:", e)