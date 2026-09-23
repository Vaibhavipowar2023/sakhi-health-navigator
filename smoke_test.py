"""Step 0 smoke test: prove that Groq + structured output works.

The pattern shown here (Pydantic schema -> with_structured_output -> validated
object, never free text) is the backbone of every LLM call in this project.
"""
import os

from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel
from langchain_groq import ChatGroq


class Greeting(BaseModel):
    message: str
    language: str


llm = ChatGroq(model=os.environ["LLM_MODEL"], temperature=0)
structured_llm = llm.with_structured_output(Greeting)

result = structured_llm.invoke("Say hello to a health navigation project, in Marathi.")
print(type(result))  # <class '__main__.Greeting'> — a validated object, not text!
print(result)
