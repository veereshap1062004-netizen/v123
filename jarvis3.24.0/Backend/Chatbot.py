from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from the .env file.
env_vars = dotenv_values(os.path.join(current_dir, "..", ".env"))

# Retrieve specific environment variables for username, assistant name, and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API key is available
if not GroqAPIKey:
    print("ERROR: GroqAPIKey not found in .env file")
    exit(1)

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list to store chat messages.
messages = []

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot.
SystemChatBot = [ 
    {"role": "system", "content": System}
]

# Create Data directory if it doesn't exist
data_dir = os.path.join(current_dir, "Data")
os.makedirs(data_dir, exist_ok=True)

# Attempt to load the chat log from a JSON file.
try:
    with open(os.path.join(data_dir, "ChatLog.json"), "r") as f:
        messages = load(f)
# Load existing messages from the chat log.
except FileNotFoundError:
    # If the file doesn't exist, create an empty JSON file to store chat logs.
    with open(os.path.join(data_dir, "ChatLog.json"), "w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n" 
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]
    # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines)
    # Join the cleaned lines back together.
    return modified_answer

def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""
    try:
        # Load the existing chat log from the JSON file.
        with open(os.path.join(data_dir, "ChatLog.json"), "r") as f:
            messages = load(f)
        
        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": f"{Query}"})

        # Use a currently available Groq model
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Updated to available model
            # Alternative models you can try:
            # model="mixtral-8x7b-32768"
            # model="gemma2-9b-it"
            # model="llama3-8b-8192"
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        # Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        
        # Append the response to the messages list.
        messages.append({"role": "assistant", "content": Answer})
        
        # Save the updated chat log to the JSON file.
        with open(os.path.join(data_dir, "ChatLog.json"), "w") as f:
            dump(messages, f, indent=4)
        
        # Return the formatted response.
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        # Handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(os.path.join(data_dir, "ChatLog.json"), "w") as f:
            dump([], f, indent=4)
        return f"Error occurred: {str(e)}"

# Function to check available models
def check_available_models():
    try:
        models = client.models.list()
        available_models = [model.id for model in models.data]
        print("Available models:", available_models)
        return available_models
    except Exception as e:
        print(f"Error checking models: {e}")
        return []

if __name__ == "__main__":
    # Check available models first
    print("Checking available models...")
    available_models = check_available_models()
    
    # Filter for commonly used models
    common_models = [model for model in available_models if any(x in model for x in ['llama', 'mixtral', 'gemma'])]
    print("Common models available:", common_models)
    
    print("\nChatbot is ready!")
    while True:
        try:
            user_input = input("Enter your question: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            if user_input.strip():
                response = ChatBot(user_input)
                print(f"Response: {response}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")