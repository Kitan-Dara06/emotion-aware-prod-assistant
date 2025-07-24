from typing import TypedDict, List, Optional, Dict
from pydantic import BaseModel

from datetime import datetime, timedelta
import pytz
import dateparser
from difflib import get_close_matches
import langchain
from openai import OpenAI
from emotion_aware_assistant.config import api_key, HUGGINGFACE_TOKEN
# import tensorflow as tf
from langchain.tools import tool
from typing import Dict
from langchain_core.runnables import RunnableLambda, RunnableBranch, RunnableMap
import json
import re
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import Literal
from pydantic import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain.prompts import  ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from requests.exceptions import ChunkedEncodingError
from langchain.agents import initialize_agent, AgentType

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from requests.exceptions import ChunkedEncodingError
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from fastapi import FastAPI, Body
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
