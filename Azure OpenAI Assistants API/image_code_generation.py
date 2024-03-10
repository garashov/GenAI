# ----------------------------------------------------------
# Libraries
# ----------------------------------------------------------
from src.logging import logging
from src.utils.utils import *
from src.utils.assistantApi_QnA import *

# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------
ARTIFACTS_PATH = "artifacts"

# ----------------------------------------------------------
# Create paths if needed
# ----------------------------------------------------------
create_path(ARTIFACTS_PATH)

# ----------------------------------------------------------
# Create an assistant
# ----------------------------------------------------------
logging.info("Creating an assistant...")
assistant = client.beta.assistants.create(
    name="Data Visualization",
    instructions=f"You are a helpful AI assistant who makes interesting visualizations based on data." 
    f"You have access to a sandboxed environment for writing and testing code."
    f"When you are asked to create a visualization you should follow these steps:"
    f"1. Write the code."
    f"2. Anytime you write new code display a preview of the code to show your work."
    f"3. Run the code to confirm that it runs."
    f"4. If the code is successful display the visualization."
    f"5. If the code is unsuccessful display the error message and try to revise the code and rerun going through the steps from above again.",
    tools=[{"type": "code_interpreter"}], # This gives the model access to a sand-boxed python environment to run and execute code to help formulating responses to a user's question.
    model=AZURE_OPENAI_GPT_35 
)
logging.info(assistant.model_dump_json(indent=2))
logging.info("-----------------------------------")

# ----------------------------------------------------------
# Create a thread
# ----------------------------------------------------------
thread = client.beta.threads.create()
logging.info(f"New Thread created with ID: {thread.id}")
logging.info("-----------------------------------")

# ----------------------------------------------------------
# Ask a question
# ----------------------------------------------------------
user_question = "Create a visualization of a sinewave"
assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=True)

# ----------------------------------------------------------
# Ask a follow-up question
# ----------------------------------------------------------
user_question = "Show me the code you used to generate the sinewave"
assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=True)

# ----------------------------------------------------------
# Ask to change the generated image
# ----------------------------------------------------------
user_question = "I prefer visualizations in darkmode can you change the colors to make a darkmode version of this visualization."
assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=True)

# ----------------------------------------------------------
# Ask to change the generated image
# ----------------------------------------------------------
user_question = "Make picture smaller"
assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=True)

# ----------------------------------------------------------
# Ask a follow-up question
# ----------------------------------------------------------
user_question = "Show me the code you used to generate latest image"
assistant_response, images_paths, code_file_paths = QnA(user_question, thread, assistant, save_path=ARTIFACTS_PATH, save_artifacts=True)

