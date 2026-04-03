import cohere
from rich import print
from dotenv import dotenv_values
import traceback
import os

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Debug: Check if environment variables are loading
print("=== DEBUGGING MODEL.PY ===")

try:
    env_vars = dotenv_values(os.path.join(current_dir, "..", ".env"))
    CohereAPIKey = env_vars.get("CohereAPIKey")
    
    if not CohereAPIKey:
        print("[red]ERROR: CohereAPIKey not found in .env file[/red]")
        print("Make sure your .env file contains: CohereAPIKey=your_actual_key_here")
        exit(1)
    else:
        print("[green]✓ API key loaded successfully[/green]")
        print(f"API Key starts with: {CohereAPIKey[:10]}...")
    
    # Test Cohere client initialization
    print("Testing Cohere client initialization...")
    co = cohere.Client(api_key=CohereAPIKey)
    print("[green]✓ Cohere client initialized successfully[/green]")
    
    # Test available models
    print("Checking available models...")
    models = co.models.list()
    available_models = [model.name for model in models.models]
    print(f"[green]✓ Available models: {available_models}[/green]")
    
    # Look for command models specifically
    command_models = [model for model in available_models if 'command' in model.lower()]
    print(f"[green]✓ Command models available: {command_models}[/green]")
    
    if not command_models:
        print("[red]ERROR: No command models found![/red]")
        exit(1)
    
    # Use the first available command model
    selected_model = command_models[0]
    print(f"[green]✓ Using model: {selected_model}[/green]")
    
except Exception as e:
    print(f"[red]ERROR: {e}[/red]")
    print("Full traceback:")
    traceback.print_exc()
    exit(1)

# If we get here, continue with the rest of the code
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search", "youtube search", "reminder"
]

messages = []
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
]

def FirstLayerDMM(prompt: str = "test"):
    try:
        messages.append({"role": "user", "content": f"{prompt}"})
        
        print(f"[blue]Sending request to model: {selected_model}[/blue]")
        
        stream = co.chat_stream(
            model=selected_model,  # Use the detected model
            message=prompt,
            temperature=0.3,  # Lower temperature for more consistent responses
            chat_history=ChatHistory,
            prompt_truncation='AUTO',  # Changed from OFF to AUTO
            preamble=preamble
        )
        
        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text
                print(f"[yellow]Streaming: {event.text}[/yellow]")
        
        print(f"[green]Raw response: {response}[/green]")
        
        response = response.replace("\n", "")
        response = response.split(",")
        response = [i.strip() for i in response]
        
        temp = []
        for task in response:
            for func in funcs:
                if task.startswith(func):
                    temp.append(task)
        
        response = temp
        
        if not response:
            print("[red]No valid functions detected in response[/red]")
            return ["general (query)"]
        
        return response
        
    except Exception as e:
        print(f"[red]Error in FirstLayerDMM: {e}[/red]")
        traceback.print_exc()
        return ["general (query)"]

if __name__ == "__main__":
    print("\n[green]=== Model is ready ===[/green]")
    print("Type your query or 'quit' to exit:")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            if user_input:
                result = FirstLayerDMM(user_input)
                print(f"[cyan]Result: {result}[/cyan]")
        except KeyboardInterrupt:
            print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            print(f"[red]Unexpected error: {e}[/red]")