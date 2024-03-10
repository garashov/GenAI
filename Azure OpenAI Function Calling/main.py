# ----------------------------------------------------------
# Libraries
# ----------------------------------------------------------
import json
from dotenv import load_dotenv
load_dotenv()

from utils import *

# ----------------------------------------------------------
# Approach 1: Simple Extraction with OpenAI function calling
# ----------------------------------------------------------
extraction_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_keywords",
            "description": "Getting keywords from the text. Do not provide any additional information out of scope.",
            "parameters": {
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "description": "Extract all mentioned  names from the text.",
                        "items": {  
                            "type": "string"
                        }
                    },
                    "projects": {
                        "type": "array",
                        "description": "Extract all mentioned projects from the text.",
                        "items": {  
                            "type": "string"
                        }
                    },
                    "cities": {
                        "type": "array",
                        "description": "Extract all mentioned cities from the text.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "weather_info": {
                        "type": "array",
                        "description": "Extract information about the weather for the corresponding location from the text.",
                        "items": {  
                            "type": "object",  
                            "properties": {  
                                "location":     {"type": "string"},  
                                "temperature":  {"type": "string"},  
                                "unit":         {"type": "string", "enum": ["celsius", "fahrenheit"]},
                            },  
                            # "required": ["location", "temperature", "unit"]
                        }     
                    },

                # "required": ["weather_info", "names", "projects", "cities],
                },
            },
        }
    }
]

prompt = """Hello, my name is Elnur and I would like to share a bit of information about this ongoing proejct named X-X-X.
I am currently in Milan and the weather is 10 degrees celsius. I am planning to go to Paris next week. Can you tell me the weather in Paris?"""

extractions = func_extraction(prompt, extraction_tools, verbose=False)

# Display the extractions
for extraction in extractions:
    print("Function:",extraction["func_name"],"\nArguments:")
    for key, value in json.loads(extraction["func_arguments"]).items():
        print(f"{key}: {value}")
    print("-"*50)


# ----------------------------------------------------------
# Approach 2: Extraction with OpenAI Function Calling and Subsequent Function Invocation
# ----------------------------------------------------------
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# Step 1: send the conversation and available functions to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location. Do not provide any additional information about the weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

history = []
# Only one function in this example, but you can have multiple
available_functions = {
    "get_current_weather": get_current_weather,
} 

# ----------------------------------------------------------
# First call
# ----------------------------------------------------------
prompt = "What's the weather like in Tokyo and Paris in celsius?"
response, history = functions_call(prompt, history, tools, available_functions, verbose=True)


# ----------------------------------------------------------
# Second call
# ----------------------------------------------------------
prompt = "What's the weather like in San Francisco in fahrenheit?"
response, history = functions_call(prompt, history, tools, available_functions, verbose=True)