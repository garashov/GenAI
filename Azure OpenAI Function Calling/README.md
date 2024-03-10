# Implementation of OpenAI Function Calling

## Table of Contents
- [Overview](#overview)
- [Description](#description)
- [Approach 1: Simple Extraction with OpenAI Function Calling](#approach-1-simple-extraction-with-openai-function-calling)
- [Approach 2: Extraction with OpenAI Function Calling and Subsequent Function Invocation](#approach-2-extraction-with-openai-function-calling-and-subsequent-function-invocation)
- [References](#references)

## Overview
This notebook demonstrates the implementation of function calling with OpenAI, focusing on the new method.
Supported version on February, 2024:
- `2023-12-01-preview`

The primary objective is to showcase how OpenAI function calling can be utilized to invoke functions based on predefined criteria and process responses accordingly.

## Description
The notebook includes two main approaches to utilize OpenAI function calling effectively:
- Approach 1: Simple Extraction with OpenAI Function Calling.
- Approach 2: Extraction with OpenAI Function Calling and Subsequent Function Invocation


## Approach 1: Simple Extraction with OpenAI Function Calling
In this approach, the notebook presents a straightforward method to extract specific keywords and information from provided text inputs. It defines a function called `extract_keywords` capable of extracting names, projects, cities, and weather information from textual data. This approach serves as a foundational step towards more advanced data processing and analysis.

## Approach 2: Extraction with OpenAI Function Calling and Subsequent Function Invocation
This approach extends the functionality of the first method by integrating function invocation based on extracted information. It involves a scenario where weather information for various locations is requested. The notebook demonstrates the process of sending a conversation prompt containing location and unit preferences to the model. Subsequently, the appropriate function (`get_current_weather`) is called based on the extracted location information. The function returns the current weather information for the specified location, which is then displayed to the user.

## Key Features
- **Flexibility**: The notebook allows for the extraction of relevant information from unstructured text inputs, enabling efficient data processing.
- **Modularity**: Functions can be easily integrated and invoked based on predefined parameters, enhancing the overall flexibility and scalability of the system.
- **Integration**: Integration with external APIs or backend services is facilitated through function calling, enabling seamless data retrieval and processing.

## Usage
Users can leverage the provided code snippets and methodologies to implement function calling with OpenAI in various applications. The notebook serves as a practical guide for harnessing the capabilities of OpenAI function calling to streamline data processing and enhance overall workflow efficiency.

For more detailed information and examples, please refer to the notebook and the provided documentation links.


## References
- [How to use function calling with Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/function-calling?tabs=python-new)