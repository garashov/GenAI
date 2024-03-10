# Implementation of OpenAI Assistants API

## Table of Contents
- [Description](#description)
- [Assistants components](#assistants-components)
- [Tools](#tools)
- [Further improvements](#further-improvements)
- [References](#references)


## Description
This repository contains the implementation of OpenAI Assistants API. 
Some features of Assistants API are:
- Allows implementation of different tools to extend the capabilities of the assistant. Examples are code_interpreter, web_search, etc.
- Allows to create custom tools using functions.
- Automatic history management and context handling (truncation to fit into the model's context).
- Automatic handling of citations.
- Adding flexibility by allowing to define custom instructions for the assistant at any moment.
- Generate and download artifacts like code, images, etc.

File `image_code_generation.py` demonstrates simple implementation of OpenAI Assistants API to generate visualizations and code snippets for a given question.
Steps of implementation are:
- Create Assistant
- Create Thread
- Pass question and Run Thread
- Get the response and artifacts.
    - Currently, code snippet extraction is not a built-in feature of the API. It is done manually.


## Assistants components
The OpenAI Assistants API is composed of the following components:
- **Assistant**: Custom AI that uses Azure OpenAI models in conjunction with tools.
- **Thread**: A conversation session between an Assistant and a user. Threads store Messages and automatically handle truncation to fit content into a model’s context.
- **Message**: A message created by an Assistant or a user. Messages can include text, images, and other files. Messages are stored as a list on the Thread.
- **Run**: Activation of an Assistant to begin running based on the contents of the Thread. The Assistant uses its configuration and the Thread’s Messages to perform tasks by calling models and tools. As part of a Run, the Assistant appends Messages to the Thread.
- **Run Step**: A detailed list of steps the Assistant took as part of a Run. An Assistant can call tools or create Messages during it’s run. Examining Run Steps allows you to understand how the Assistant is getting to its final results.


## Tools
- An individual assistant can access up to 128 tools including code interpreter.
- You can define your own custom tools via [functions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistant-functions?tabs=python).


## Further improvements:
- Understand Annotations and how to use them.
- Upload file for Code Interpreter/individual thread.
- Use Assistant API to upload files and create a chatbot with RAG.
    - There can be a maximum of 20 files attached to the assistant. Files are ordered by their creation date in ascending order.
- Try other different tools.
- Define custom function for tools to use with Assistant API.


## References
- [Getting started with Azure OpenAI Assistants](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistant)
- [Azure OpenAI Assistants Code Interpreter](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/code-interpreter?tabs=python)
- [Azure OpenAI Assistants function calling](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistant-functions?tabs=python)
- [Azure OpenAI Assistans Supported models](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#assistants-preview)
- [Open AI Tools Code Interpreter](https://platform.openai.com/docs/assistants/tools/code-interpreter)
- [Assistants API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/assistants-reference?tabs=python)