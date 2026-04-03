from webbrowser import open as webopen
from pywhatkit import search
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import platform
import keyboard
import asyncio
import os
import sys
import psutil
import signal

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables
env_vars = dotenv_values(os.path.join(current_dir, "..", ".env"))
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API key is available
if not GroqAPIKey:
    print("ERROR: GroqAPIKey not found in .env file")
    exit(1)

classes = [
    "zCubwf", "IZ6rdc", "hgKElc", "LTKOO sYric", "ZOLcW", "grt vk_bk Fzwsb YwPhnf", 
    "polqee", "tw-Data-text tw-text-small tw-ta", "05uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need don't hesitate to ask.",
]

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        # Cross-platform text editor opening
        if platform.system() == "Windows":
            subprocess.Popen(["notepad.exe", File])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", "-t", File])  # Opens in default text editor
        else:  # Linux
            subprocess.Popen(["xdg-open", File])
    
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriterAI(Topic)
    
    # Create Data directory if it doesn't exist
    data_dir = os.path.join(current_dir, "Data")
    os.makedirs(data_dir, exist_ok=True)
    
    filename = Topic.lower().replace(' ', '_') + ".txt"
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    
    OpenNotepad(filepath)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    # Removed automatic YouTube video playing
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" # Constructthe Youtube search URL.
    webbrowser.open(Url4Search)
# Open the search URL in a web browser.
    return True
def find_running_apps(app_name):
    """Find running processes that match the app name"""
    running_processes = []
    app_name_lower = app_name.lower()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check process name
            if app_name_lower in proc.info['name'].lower():
                running_processes.append(proc)
                continue
                
            # Check command line
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline']).lower()
                if app_name_lower in cmdline:
                    running_processes.append(proc)
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return running_processes

def CloseApp(app_name):
    """Enhanced app closing function for all platforms"""
    print(f"🔄 Attempting to close: {app_name}")
    
    try:
        # Common app mappings for different platforms
        app_mappings = {
            # macOS applications
            "safari": "Safari",
            "chrome": "Google Chrome",
            "firefox": "Firefox", 
            "notes": "Notes",
            "calculator": "Calculator",
            "calendar": "Calendar",
            "messages": "Messages",
            "mail": "Mail",
            "music": "Music",
            "tv": "TV",
            "photos": "Photos",
            "preview": "Preview",
            "terminal": "Terminal",
            "finder": "Finder",
            
            # Windows applications
            "notepad": "notepad.exe",
            "calculator": "Calculator.exe",
            "paint": "mspaint.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            
            # Browser processes
            "browser": ["Google Chrome", "Safari", "Firefox", "Microsoft Edge"]
        }
        
        # Get the actual app name from mappings
        target_app = app_mappings.get(app_name.lower(), app_name)
        
        # Find running processes
        running_processes = find_running_apps(target_app)
        
        if not running_processes:
            print(f"❌ No running processes found for: {app_name}")
            return False
        
        closed_count = 0
        for proc in running_processes:
            try:
                print(f"🛑 Closing process: {proc.info['name']} (PID: {proc.info['pid']})")
                
                if platform.system() == "Windows":
                    proc.kill()
                else:
                    # macOS and Linux
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)  # Wait for process to terminate
                    except psutil.TimeoutExpired:
                        proc.kill()  # Force kill if not terminated
                
                closed_count += 1
                print(f"✅ Successfully closed: {proc.info['name']}")
                
            except Exception as e:
                print(f"❌ Error closing {proc.info['name']}: {e}")
        
        if closed_count > 0:
            print(f"✅ Closed {closed_count} processes for: {app_name}")
            return True
        else:
            print(f"❌ Failed to close any processes for: {app_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error in CloseApp for {app_name}: {e}")
        return False

def OpenApp(app_name, sess=requests.Session()):
    """Enhanced app opening function"""
    print(f"🔄 Attempting to open: {app_name}")
    
    try:
        #appopen(app, match_closest=True, output=True, throw_error=True)
        #return True

        # Common app mappings
        app_commands = {
            # macOS applications
            "safari": "open -a Safari",
            "chrome": "open -a 'Google Chrome'", 
            "firefox": "open -a Firefox",
            "notes": "open -a Notes",
            "calculator": "open -a Calculator",
            "calendar": "open -a Calendar",
            "messages": "open -a Messages",
            "mail": "open -a Mail",
            "music": "open -a Music",
            "photos": "open -a Photos",
            "preview": "open -a Preview",
            "terminal": "open -a Terminal",
            "textedit": "open -a TextEdit",
            "calculator": "open -a Calculator",
            
            # Windows applications  
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "cmd": "cmd",
            "browser": "start https://www.google.com"
        }
        
        # Check if we have a direct command
        app_lower = app_name.lower()
        if app_lower in app_commands:
            command = app_commands[app_lower]
            print(f"🎯 Using predefined command: {command}")
            
            if platform.system() == "Windows":
                if command.startswith("open -a"):
                    # Convert macOS command to Windows
                    if "safari" in app_lower or "chrome" in app_lower or "firefox" in app_lower:
                        subprocess.Popen(["start", "https://www.google.com"], shell=True)
                    else:
                        subprocess.Popen(command.split()[2:], shell=True)
                else:
                    subprocess.Popen(command, shell=True)
            else:
                # macOS/Linux
                subprocess.Popen(command.split(), shell=False)
            
            print(f"✅ Opened: {app_name}")
            return True
        
        # Try to open as a website if it contains common TLDs
        if any(ext in app_lower for ext in ['.com', '.org', '.net', '.io']):
            if not app_lower.startswith(('http://', 'https://')):
                app_name = 'https://' + app_name
            webbrowser.open(app_name)
            print(f"🌐 Opened website: {app_name}")
            return True
        
        # Try system-specific methods
        if platform.system() == "Windows":
            try:
                subprocess.Popen([app_name], shell=True)
                print(f"✅ Opened Windows app: {app_name}")
                return True
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                subprocess.Popen(["open", "-a", app_name])
                print(f"✅ Opened macOS app: {app_name}")
                return True
            except:
                pass
        
        # Fallback: web search for the app
        print(f"🔍 Could not open directly, searching web for: {app_name}")
        search_url = f"https://www.google.com/search?q={app_name}"
        webbrowser.open(search_url)
        return True
        
    except Exception as e:
        print(f"❌ Error opening app {app_name}: {e}")
        return False

def System(command):
    def mute():
        if platform.system() == "Windows":
            keyboard.press_and_release("volume mute")
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["osascript", "-e", "set volume output muted true"])
        # Linux volume control would require additional libraries
    
    def unmute():
        if platform.system() == "Windows":
            keyboard.press_and_release("volume mute")
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["osascript", "-e", "set volume output muted false"])
    
    def volume_up():
        if platform.system() == "Windows":
            keyboard.press_and_release("volume up")
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    
    def volume_down():
        if platform.system() == "Windows":
            keyboard.press_and_release("volume down")
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
    
    command = command.strip().lower()
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    results = []
    
    for command in commands:
        command = command.strip()
        print(f"🔧 Processing command: {command}")
        
        if command.startswith("open"):
            if "open it" in command or "open file" in command:
                pass
            else:
                app_name = command.replace("open", "").strip()
                print(f"🚀 Opening app: {app_name}")
                fun = asyncio.to_thread(OpenApp, app_name)
                funcs.append(fun)
                
        elif command.startswith("close"):
            app_name = command.replace("close", "").strip()
            print(f"🛑 Closing app: {app_name}")
            fun = asyncio.to_thread(CloseApp, app_name)
            funcs.append(fun)
            
        elif command.startswith("play "):
            song_name = command.replace("play", "").strip()
            fun = asyncio.to_thread(PlayYoutube, song_name)
            funcs.append(fun)
            
        elif command.startswith("content "):
            topic = command.replace("content", "").strip()
            fun = asyncio.to_thread(Content, topic)
            funcs.append(fun)
            
        elif command.startswith("google search "):
            search_term = command.replace("google search", "").strip()
            fun = asyncio.to_thread(GoogleSearch, search_term)
            funcs.append(fun)
            
        elif command.startswith("youtube search "):
            search_term = command.replace("youtube search", "").strip()
            fun = asyncio.to_thread(YouTubeSearch, search_term)
            funcs.append(fun)
            
        elif command.startswith("system "):
            sys_command = command.replace("system", "").strip()
            fun = asyncio.to_thread(System, sys_command)
            funcs.append(fun)
            
        else:
            print(f"❌ No function found for: {command}")
    
    # Execute all functions
    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error in task {i}: {result}")
            else:
                print(f"✅ Task {i} completed: {result}")
    
    return results

async def Automation(commands: list[str]):
    print(f"🤖 Starting automation with commands: {commands}")
    results = await TranslateAndExecute(commands)
    print(f"🏁 Automation completed. Results: {results}")
    return True

# Test function
async def test_close_app():
    """Test the close app functionality"""
    print("🧪 Testing close app functionality...")
    
    # Test closing common apps
    test_apps = ["safari", "chrome", "calculator", "notes"]
    
    for app in test_apps:
        print(f"\n🔍 Testing close for: {app}")
        result = await asyncio.to_thread(CloseApp, app)
        print(f"Result: {'✅ Success' if result else '❌ Failed'}")

if __name__ == "__main__":
    print(f"🖥️ Running on: {platform.system()}")
    
    if platform.system() == "Darwin":
        print("🍎 macOS detected - some features may require permissions")
    
    # Test the close app functionality
    import asyncio
    asyncio.run(test_close_app())