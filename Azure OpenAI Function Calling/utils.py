# ----------------------------------------------------------
# Libraries
# ----------------------------------------------------------
import os
import json
from openai import AzureOpenAI


# ----------------------------------------------------------
# Get environment variables
# ----------------------------------------------------------
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
# AZURE_OPENAI_GPT_35 = os.getenv("AZURE_OPENAI_GPT_35")
AZURE_OPENAI_GPT_4T = os.getenv("AZURE_OPENAI_GPT_4T")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,  
    api_version=AZURE_OPENAI_VERSION,
    azure_endpoint = AZURE_OPENAI_SERVICE
    )


# ----------------------------------------------------------
# Functions
# ----------------------------------------------------------
def func_extraction(prompt, tools, verbose=False):
    """
    Function to extract the information from the text with help of OpenAI function calling.
    This function extracts the information from text without further need to perform additional steps 
    such as calling other services/APIs.
    Here we do not manage the historical messages bcs of simple text extraction logic, but it is feasible.
    """
    prompt = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model=AZURE_OPENAI_GPT_4T,
        messages=prompt,
        tools=tools,
        # tool_choice="auto",
        tool_choice={"type": "function", "function": {"name": "extract_keywords"}}, 
        
    )

    extractions = []
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            data = {"func_name" : tool_call.function.name,
                    "func_arguments" : tool_call.function.arguments}
            extractions.append(data)
    if verbose:
        print(json.dumps(extractions, indent=2))
    return extractions



def functions_call(prompt, history, tools, available_functions, verbose=False):
    """
    Function to call the OpenAI model to get functions that need to be called (such as def, API, etc.).
    After that, it calls all required functions and then sends the information back to the model to 
    generate the final response.
    For example, if the model asks for the weather, this function will call the weather API and then
    send the response back to the model.
    For this example, we have a hardcoded function to return the same weather always (more like a mock API).
    """
    prompt = {"role": "user", "content": prompt}
    history.append(prompt)
    messages = [prompt]
    final_prompt = history[-11:-1] + messages
    if verbose:
        print(json.dumps(final_prompt, indent=2))

    response = client.chat.completions.create(
        model=AZURE_OPENAI_GPT_4T,
        messages=final_prompt,
        tools=tools,
        tool_choice="auto",
        # tool_choice={"type": "function", "function": {"name": "extract_keywords"}}, 
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if verbose:
        print(dict(response_message))

    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        # Take last 10 messages except the last one of history and all messages from the tool calls
        final_prompt = history[-11:-1] + messages
        if verbose:
            print(final_prompt)
        second_response = client.chat.completions.create(
            model=AZURE_OPENAI_GPT_4T,
            messages=final_prompt,
        )  # get a new response from the model where it can see the function response

    response = second_response.choices[0].message.content
    role = second_response.choices[0].message.role

    history.append({"role": role, "content": response})
    if verbose:
        print(json.dumps(history, indent=2))
        print(response)
    return response, history