from django.db import models

# Create your models here.
# D:\cognito_ai_assistant\ai_core\models.py (New File for Model Definitions)

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# TIER 1: Low-Cost/Fast for simple classification
MODERATOR_LLM = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.0)

# TIER 2: Speed/Balance for primary execution
# GPT-4o Mini is a good choice for balanced performance
EXECUTION_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# TIER 3: High-Capability/Judge for complex evaluation (Highest Cost)
JUDGE_LLM = ChatOpenAI(model="gpt-4-turbo", temperature=0.0) 

# Example of a non-OpenAI model for diversity/redundancy
PLANNER_LLM = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.1)