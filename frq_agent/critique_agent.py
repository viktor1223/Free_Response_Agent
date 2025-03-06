from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class CritiqueAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.message_history = [
            SystemMessage(content="""You are an AP Free Response Evaluator.
            Your role is to:
            - Evaluate student responses against AP scoring guidelines
            - Identify key concepts demonstrated or missing
            - Provide specific, actionable feedback
            - Highlight areas for improvement
            - Score responses on typical AP 0-4 point scale per section
            - Consider both code correctness and style""")
        ]

    def evaluate_response(self, frq_question: str, student_response: str) -> str:
        evaluation_prompt = f"""
        Question:
        {frq_question}

        Student Response:
        {student_response}

        Evaluate this response considering:
        1. Correctness of implementation
        2. Proper use of programming concepts
        3. Code style and organization
        4. Completeness of answer
        
        Provide:
        - Point-by-point scoring
        - Specific feedback for improvement
        - Overall assessment
        """
        
        self.message_history.append(HumanMessage(content=evaluation_prompt))
        response = self.llm(self.message_history)
        self.message_history.append(response)
        
        return response.content

    def reset_history(self):
        """Reset conversation to initial system prompt"""
        self.message_history = [self.message_history[0]]