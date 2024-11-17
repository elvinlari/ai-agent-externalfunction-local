# agent.py

import anthropic
import os

# set up the Antrhopic API key
if not os.getenv("ANTHROPIC_API_KEY"):
    os.environ["ANTHROPIC_API_KEY"] = input("Please enter your Anthropics API key: ") # Prompt the user to enter their API key

# Create the Anthropic client
client = anthropic.Anthropic()
sonnet = "claude-3-opus-20240229"



def score_checker(score):
    if score > 50:
        return "Pass"
    else:
        return "Fail"
    


# Create the Analyzer Agent
def analyzer_agent(sample_data):
    message = client.messages.create(
        model=sonnet,
        max_tokens=400, # limit the response to 400 tokens
        temperature=1, # set a low temprature for more focussed deterministic output
        system="You are an AI agent analysing scores", # Use the predefined system prompt for the analyzer agent
        tools=[
            {
                "name": "score_checker",
                "description": "A function that takes the score provided and return the results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "string"}
                    },
                    "required": ["score"],
                },
            }
        ],
        messages=[
            {
                "role": "user",
                "content": sample_data
            }
        ]
    )
    return message


# Confirm the tool to use
def confirmation(message):
    dataFromCustomFunction = None
    if message.stop_reason == "tool_use":
        tool_params = message.content[1].input
        tool_name = message.content[1].name
    
    # call available tool function
    if tool_name == "score_checker":
        result = score_checker(float(tool_params["score"]))
        dataFromCustomFunction = result
        print(result)
    return dataFromCustomFunction


# Respond in natural language
def respond(dataFromCustomFunction):
    response = client.messages.create(
        model=sonnet,
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": "Answer to the customer. The customer exam status is " + dataFromCustomFunction
            }
        ]
    )
    return response.content[0].text


# Get input from user
sample_data = input("Enter the score you want to analyze and include a description: ")

# Call the analyzer agent
result = analyzer_agent(sample_data)
print("\n---------------------------------------------\n\nAnalysing data...")

# Check the score and print the result
result = confirmation(result)
print("\n---------------------------------------------\n\nGenerating response...")

# Respond to the user
result = respond(result)

# Print the result
print(f"\nAnalysis Result\n: {result}")
