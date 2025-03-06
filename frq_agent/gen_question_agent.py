from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

import sqlite3  

from utils import execute_query

class Generate_FRQ:
    def __init__(self):
        self.agent = None 
        self.foundational_llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.db_path = "data/metadata.db"
        self.message_history = [
            SystemMessage(content="""You are an AP FRQ Generator.
            Your role is to generate free response questions that:
            - Match AP exam style and difficulty
            - Test key programming concepts
            - Include clear setup and requirements
            - Break problems into multiple parts
            - Follow standard AP scoring guidelines""")
        ]

    def get_avilable_topics(self):
        query = "SELECT class_name FROM classes"
        try:
            topics = execute_query(self.db_path, query)
            return [topic[0] for topic in topics]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def gen_FRQ(self, selected_topic: str) -> str:
        self.reset_history()  # Start fresh for each generation
        
        # Get example FRQs for reference
        query = """
        SELECT f.frq 
        FROM frq f 
        JOIN classes c ON f.class_id = c.class_id 
        WHERE c.class_name = ?
        """
        frq_examples = execute_query(self.db_path, query, (selected_topic,))
        
        # Generate new FRQ using examples as reference
        base_prompt = f"""Generate an AP-style Free Response Question for {selected_topic}.
        Use these example FRQs as reference for style and format:
        {[example[0] for example in frq_examples]}
        """
        
        self.message_history.append(SystemMessage(content=base_prompt))
        response = self.foundational_llm(self.message_history)
        self.message_history.append(response)
        
        return response.content

    def reset_history(self):
        """Reset conversation to initial system prompt"""
        self.message_history = [self.message_history[0]]