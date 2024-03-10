import os
import autogen
from dotenv import load_dotenv
load_dotenv()

print(autogen.__version__)


AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_KEY"]
AZURE_OPENAI_VERSION = os.environ["AZURE_OPENAI_VERSION"]
AZURE_OPENAI_DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]


config_list = [
    {
        'model': AZURE_OPENAI_DEPLOYMENT,
        'api_key': AZURE_OPENAI_KEY,
        'base_url': AZURE_OPENAI_ENDPOINT,
        'api_type': 'azure',
        'api_version': AZURE_OPENAI_VERSION,
    }
]

llm_config={
    # "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0
}

assistant = autogen.AssistantAgent(
    name="CTO",
    llm_config=llm_config,
    system_message="Chief technical officer of a tech company"
)
# assistant2 = autogen.AssistantAgent(
#     name="CEO",
#     llm_config=llm_config,
#     system_message="***"
# )

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",                   # Other options: "ALWAYS", "TERMINATE", "NEVER"
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
# Otherwise, reply with the reason why the task is not solved yet."""
#     system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
# Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

task = """
Give me a summary of article: https://microsoft.github.io/autogen/docs/FAQ/#set-your-api-endpoints
"""

user_proxy.initiate_chat(
    assistant,
    message=task
)

task2 = """
Change the code in the file you just created to instead output numbers 1 to 200
"""

user_proxy.initiate_chat(
    assistant,
    message=task2
)