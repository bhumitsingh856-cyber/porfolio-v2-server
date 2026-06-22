from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-120b")
embedding_model = NVIDIAEmbeddings(model="nvidia/nv-embed-v1")