from Frontend.GUI import( 
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus )
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

env_vars = dotenv_values(os.path.join(current_dir, ".env"))
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'{Username}: Hello {Assistantname}, How are you?\n{Assistantname}: Welcome {Username}. I am doing well. How may i help you?'
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    chatlog_path = os.path.join(current_dir, "Backend", "Data", "ChatLog.json")
    try:
        with open(chatlog_path, "r", encoding='utf-8') as file:
            content = file.read()
            if len(content) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except FileNotFoundError:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    chatlog_path = os.path.join(current_dir, "Backend", "Data", "ChatLog.json")
    try:
        with open(chatlog_path, 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ") 
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            Data = file.read()
        if len(str(Data)) > 0:
            lines = Data.split('\n')
            result = '\n'.join(lines)
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(result)
    except FileNotFoundError:
        pass

def InitialExecution():
    SetMicrophoneStatus("False") 
    ShowTextToScreen("") 
    ShowDefaultChatIfNoChats() 
    ChatLogIntegration() 
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False 
    ImageExecution = False 
    ImageGenerationQuery = ""
    
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking... ")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")
    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )
    for queries in Decision:
        if "generate " in queries: 
            ImageGenerationQuery = str(queries) 
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision))) 
                TaskExecution = True

    if ImageExecution==True:
        # Clean the image generation query
        clean_query = ImageGenerationQuery.replace("generate image ", "").strip()
        with open(os.path.join(current_dir, "Frontend", "Files", "ImageGeneration.data"), "w") as file: 
            file.write(f"{clean_query},True")
        print(f"📝 Written to ImageGeneration.data: {clean_query},True")

        try:
            # Use sys.executable to get the current Python executable
            image_generation_script = os.path.join(current_dir, 'Backend', 'ImageGeneration.py')
            print(f"🚀 Starting ImageGeneration.py: {image_generation_script}")
            
            # Use the same Python executable that's running Main.py
            p1 = subprocess.Popen([sys.executable, image_generation_script], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                stdin=subprocess.PIPE, shell=False) 
            subprocesses.append(p1)
            print("✅ ImageGeneration.py started successfully")

        except Exception as e:
            print(f"❌ Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ... ")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname}{Answer}")
        SetAssistantStatus("Answering ... ")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking... ") 
                QueryFinal = Queries.replace("general ","") 
                Answer = ChatBot(QueryModifier(QueryFinal)) 
                ShowTextToScreen(f"{Assistantname} : {Answer}") 
                SetAssistantStatus("Answering ... ") 
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching... ") 
                QueryFinal = Queries.replace("realtime ","") 
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal)) 
                ShowTextToScreen(f"{Assistantname}: {Answer}") 
                SetAssistantStatus("Answering... ") 
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering ... ") 
                TextToSpeech(Answer) 
                SetAssistantStatus("Answering... ") 
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()

        else:
            AIStatus = GetAssistantStatus()
            if "Available ... " in AIStatus:
                sleep(0.1)

            else:
                SetAssistantStatus("Available ... ")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True) 
    thread2.start()
    SecondThread()