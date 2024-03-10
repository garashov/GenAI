import json
import os
import time
from src.logging import logging
from IPython.display import clear_output
from io import BytesIO
from PIL import Image
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------------------------
# Get environment variables
# ----------------------------------------------------------
AZURE_OPENAI_SERVICE = os.getenv("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_GPT_35 = os.getenv("AZURE_OPENAI_GPT_35")
# AZURE_OPENAI_GPT_4T = os.getenv("AZURE_OPENAI_GPT_4T")
AZURE_OPENAI_VERSION = os.getenv("AZURE_OPENAI_VERSION")

# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,  
    api_version=AZURE_OPENAI_VERSION,
    azure_endpoint = AZURE_OPENAI_SERVICE
    )


def wait_for_run_to_complete(thread, run):
    # start_time = time.time()
    status = run.status
    logging.info("Looping till the run is completed/expired/cancelled/failed...")
    while status not in ["completed", "cancelled", "expired", "failed"]:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id,run_id=run.id)
        # logging.info("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60), int((time.time() - start_time) % 60)))
        status = run.status
        # logging.info(f'Status: {status}')
        clear_output(wait=True)
    logging.info("Run completed")
    logging.info(f'Final run status: {status}')
    logging.info("-----------------------------------")


def get_latest_responses(data):
    # Collect the latest user question
    for idx,message in enumerate(data['data']):
        if message['role'] == 'user':
            break
    return data['data'][:idx]

def get_QnA(latest_messages):
    """
    Extracts the user's question and the assistant's textual responses from the latest messages.
    """
    assistant_response = ""

    # Collect all assistant responses into a string
    for message in reversed(latest_messages):
        if message['role'] == 'assistant':
            for content in message['content']:
                if content['type'] == 'text':
                    assistant_response += content['text']['value'] + "\n"
    return assistant_response

def extract_code_snippet(text):
    # Split the text by "```"
    code_blocks = text.split("```")

    # Check if there are exactly two code blocks
    if len(code_blocks) != 3:
        # print("There is no code block or there is more that one code block.")
        return None, None

    # Extract code snippet and extension
    code_snippet = '\n'.join(code_blocks[1].splitlines()[1:]) 
    extension = code_blocks[1].split("\n")[0].strip().lower()  # Normalize extension to lowercase
    if extension in ["python", "py"]:
        extension = "py"

    # Check if the code snippet and extension are valid
    if not code_snippet:
        # print("Got and empty code snippet after extraction")
        return None, None
    elif extension != "py":
        # print("Unsupported language. Only Python is supported.")
        return None, None
    return code_snippet, extension  # Return the code snippet and standardized extension

def get_artifacts(messages, save_path=None, save_artifacts=False):
    images_paths = []
    code_file_paths = []
    for message in messages:
        # TODO: Currently not checking/logging keys file_ids, metadata -  empty for now.
        message_id = message['id']
        role = message['role']
        if role == 'assistant':
            for content in message['content']:
                content_type = content['type']
                # TODO: manage other possible content types: currently handling text, code and image files.
                # logging.info(json.dumps(content, indent=2))  
                if content_type == 'text':
                    text = content['text']['value']
                    annotations = content['text']['annotations']
                    # Extract with regex generated code snippet if there is one.
                    code_snippet, extension = extract_code_snippet(text)
                    if code_snippet:
                        logging.info(f'Extracting code snippet...')
                        # Display the code snippet
                        logging.info(f'Code Extension: {extension}')
                        logging.info(f'Code Snippet:\n {code_snippet}')

                        # Save the code snippet to a file
                        if save_artifacts:
                            code_file_path = f"{save_path}/{message_id}.{extension}"
                            with open(code_file_path, "w") as file:
                                file.write(code_snippet)
                            logging.info(f"Saved code snippet to {code_file_path}")
                            code_file_paths.append(code_file_path)
                    # TODO: perform annotations processing. Currently are None.
                    if annotations:
                        logging.info(f'Annotations: {annotations}')

                elif content_type == 'image_file':
                    image_file_id = content['image_file']['file_id']
                    logging.info(f'Image File ID: {image_file_id}')

                    # # Get the image file object
                    # image_file = client.files.retrieve(image_file_id)
                    # logging.info(image_file.model_dump_json(indent=2))

                    # Get the image content in bytes
                    image_data = client.files.content(image_file_id)
                    image_data_bytes = image_data.read()

                    if save_artifacts:
                        # Download image
                        img_path = f"{save_path}/{image_file_id}.png"
                        with open(img_path, "wb") as file:
                            file.write(image_data_bytes)
                        logging.info(f"Saved image to {img_path}")
                        images_paths.append(img_path)
                    # Display the image
                    img = Image.open(BytesIO(image_data_bytes))
                    display(img)
    logging.info("-----------------------------------")
    return images_paths, code_file_paths


def QnA(user_question, thread, assistant, save_path=None, save_artifacts=False):
    # ----------------------------------------------------------
    # Pass user's question to the thread
    # ----------------------------------------------------------
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_question
    )
    # Display the thread messages to check the user question
    messages = client.beta.threads.messages.list(thread.id)
    print(messages.model_dump_json(indent=2))

    # ----------------------------------------------------------
    # Run thread
    # ----------------------------------------------------------
    logging.info("New question arrived. Running thread...")

    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    #instructions="New instructions" #You can optionally provide new instructions but these will override the default instructions
    )
    # Wait for the run to complete
    wait_for_run_to_complete(thread, run)

    # Input and output logs of Code Interpreter
    run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
    )
    print(run_steps.model_dump_json(indent=2))

    # ----------------------------------------------------------
    # Get the messages with the generated response
    # ----------------------------------------------------------
    messages = client.beta.threads.messages.list(
    thread_id=thread.id
    ) 
    print(messages.model_dump_json(indent=2))

    # ----------------------------------------------------------
    # Parse the messages to get generated response and artifacts
    # ----------------------------------------------------------
    data = json.loads(messages.model_dump_json(indent=2))
    n_messages = len(data['data'])
    logging.info(f'Total number of messages: {n_messages}')
    logging.info(f'Latest user question: {user_question}')

    # Filter the messages to the latest user's question and assistant's responses
    latest_messages = get_latest_responses(data)

    # Get user question and assistant's responses
    assistant_response = get_QnA(latest_messages)
    logging.info(f"Latest Assistant Responses:\n{assistant_response}")

    # Extract the artifacts from the messages
    images_paths, code_file_paths = get_artifacts(latest_messages, save_path=save_path, save_artifacts=save_artifacts)
    return assistant_response, images_paths, code_file_paths


### EXAMPLE OF USAGE:
if __name__ == "__main__":
    data = {'data': [
        {'id': 'msg_hGSUXCSQMvDvLp4gAShLB4BM',
    'assistant_id': 'asst_Rzys3SSEQUDQr2Ei0t8AH5N0',
    'content': [{'text': {'annotations': [],
        'value': "Sure, here is the code that was used to generate the sine wave:\n\n```python\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# Generate a sine wave\nx = np.linspace(0, 4 * np.pi, 1000)  # from 0 to 4*pi with 1000 points\ny = np.sin(x)\n\n# Plot the sine wave\nplt.figure(figsize=(10, 4))\nplt.plot(x, y, label='sin(x)')\nplt.title('Sine Wave')\nplt.xlabel('x')\nplt.ylabel('y')\nplt.legend()\nplt.grid(True)\nplt.show()\n```\n\nThe code generates an array of x values from 0 to 4π and calculates the sine of each x value to produce a smooth sine wave. The result is then plotted using Matplotlib with appropriate labels and a grid to aid in visualization."},
        'type': 'text'}],
    'created_at': 1708350215,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'assistant',
    'run_id': 'run_GAY950Y7PDjved3bNIhAo7Kc',
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'},
    {'id': 'msg_6yDgO0BuxV7C2eIwDT0KOrWv',
    'assistant_id': None,
    'content': [{'text': {'annotations': [],
        'value': 'Show me the code you used to generate the sinewave'},
        'type': 'text'}],
    'created_at': 1708350214,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'user',
    'run_id': None,
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'},
    {'id': 'msg_Sp72lG3i7tVsxnzqTf5IukoS',
    'assistant_id': 'asst_Rzys3SSEQUDQr2Ei0t8AH5N0',
    'content': [{'image_file': {'file_id': 'assistant-FHkqnBD4jO7xnwTEYeCPg5Fb'},
        'type': 'image_file'},
        {'text': {'annotations': [],
        'value': 'The sine wave visualization has been created successfully. The plot shows one complete cycle of a sinusoidal curve, which corresponds to the mathematical function sin(x) over the domain from 0 to 4π.'},
        'type': 'text'}],
    'created_at': 1708350163,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'assistant',
    'run_id': 'run_FTkeiS4VWtDtvHnt2RmGhjcd',
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'},
    {'id': 'msg_4XlBr5L24M4Was3j376AnvNn',
    'assistant_id': 'asst_Rzys3SSEQUDQr2Ei0t8AH5N0',
    'content': [{'text': {'annotations': [],
        'value': "It appears that the internal error continues to occur when attempting to generate the sine wave visualization. I will attempt to resolve this by varying the approach or simplifying the code. Let's try one more time."},
        'type': 'text'}],
    'created_at': 1708350146,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'assistant',
    'run_id': 'run_FTkeiS4VWtDtvHnt2RmGhjcd',
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'},
    {'id': 'msg_eEsZ266I72UyYiHg64KdofIL',
    'assistant_id': 'asst_Rzys3SSEQUDQr2Ei0t8AH5N0',
    'content': [{'text': {'annotations': [],
        'value': "It seems I encountered an internal error while attempting to generate the visualization. Let's try running the code again to see if the issue persists."},
        'type': 'text'}],
    'created_at': 1708350136,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'assistant',
    'run_id': 'run_FTkeiS4VWtDtvHnt2RmGhjcd',
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'},
    {'id': 'msg_IJJLxxowkZ15ad5wbrkS7MSY',
    'assistant_id': None,
    'content': [{'text': {'annotations': [],
        'value': 'Create a visualization of a sinewave'},
        'type': 'text'}],
    'created_at': 1708350117,
    'file_ids': [],
    'metadata': {},
    'object': 'thread.message',
    'role': 'user',
    'run_id': None,
    'thread_id': 'thread_af0mv9FtWUlSnHoGOmDGBdAI'}],
    'object': 'list',
    'first_id': 'msg_hGSUXCSQMvDvLp4gAShLB4BM',
    'last_id': 'msg_IJJLxxowkZ15ad5wbrkS7MSY',
    'has_more': False}

    FOLDER_ARTIFACTS = "artifacts"
    latest_messages = get_latest_responses(data)
    assistant_response = get_QnA(latest_messages)
    images_paths, code_file_paths = get_artifacts(latest_messages, save_path=FOLDER_ARTIFACTS, save_artifacts=True)
    code_snippet, extension = extract_code_snippet(assistant_response)
    # assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=TRUE)
