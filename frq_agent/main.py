from gen_question_agent import Generate_FRQ
from critique_agent import CritiqueAgent

import os 
import getpass 

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

gen_FRQ = Generate_FRQ()
critic = CritiqueAgent()

available_topics = gen_FRQ.get_avilable_topics()
print(available_topics)
user_input = available_topics[0]#input("Enter a topic: ")

frq_question = gen_FRQ.gen_FRQ(user_input)

user_input = gen_FRQ.foundational_llm(frq_question + "write an resposne to answer this question")
print(user_input)

feedback = critic.evaluate_response(frq_question, user_input)
print(feedback)