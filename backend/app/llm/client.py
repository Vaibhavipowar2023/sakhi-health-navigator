"""Groq LLM client. Single instance, shared by all agents."""
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0) -> ChatGroq:
    return ChatGroq(
        model=os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=temperature,
    )
