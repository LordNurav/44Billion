import os
from dotenv import load_dotenv
import gradio as gr
import requests
#from langchain.chat_models import AzureChatOpenAI
from langchain_community.chat_models import AzureChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from azure.cosmosdb.table.tableservice import TableService
import pandas as pd
import langchain
from langchain.chains.question_answering import load_qa_chain
#from langchain.document_loaders import WebBaseLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
#from langchain.llms import AzureOpenAI
from langchain_community.llms import AzureOpenAI
from translate import Translator
from azure.cosmosdb.table.tableservice import TableService
import pandas as pd


langchain.debug = True
load_dotenv()

# Create instance to call GPT model
gpt = AzureChatOpenAI(
    #openai_api_base=
    azure_endpoint=os.environ.get("openai_endpoint"),
    openai_api_version="2023-03-15-preview",
    deployment_name=os.environ.get("gpt_deployment_name"),
    openai_api_key=os.environ.get("openai_api_key"),
    openai_api_type = os.environ.get("openai_api_type"),
)

def call_gpt_model(message):
    system_template="You are a professional creative artistic consultant designed to help come up with ideas for artistic expression given whatever objects are at the user's disposal.  \n"
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    user_prompt=PromptTemplate(
        template="## Considering all information you have at your disposal, provide ideas given the objects below, giving as much specific detail as possible.\n" +
                "## Objects: \n {message} \n",
        input_variables=["message"],
    )
    human_message_prompt = HumanMessagePromptTemplate(prompt=user_prompt)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    # Get formatted messages for the chat completion
    messages = chat_prompt.format_prompt(message={message}).to_messages()

    # Call the model
    output = gpt(messages)
    return output.content

def call_langchain_model(user_ask):
    qa_template = """
        # Reference documentation
        {context} 
        # Question 
        {question}
        # Answer
    """
    PROMPT = PromptTemplate(
        template=qa_template, input_variables=["context", "question"]
    )
    llm = AzureChatOpenAI(deployment_name=os.environ.get("gpt_deployment_name"), 
                        openai_api_version="2023-05-15",
                        temperature=0,
                        openai_api_key=os.environ.get("openai_api_key"),
                        openai_api_base=os.environ.get("openai_endpoint"))

    chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)
    result = chain({"question": user_ask}, return_only_outputs=True)
    #print(result)
    return result["output_text"]

def scrape(urls):
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return docs

def chat(message):
    
    #urls = [x for x in urls_list if x is not None and x != "NaN"]
     
    #bing_response = bingsearch.call_search_api(query, bing_endpoint, bing_api_key)
    #rag_from_bing = bing_response
    #rag_from_bing = ""

    #docs = scrape(urls)
    
    #langchain_response = call_langchain_model(rag_from_bing, message)

    langchain_response = call_langchain_model(message)
    
    # Call GPT model with context from Bing
    #model_response =call_gpt_model(rag_from_bing, message)
    #return model_response
    return langchain_response


# Gets the ip address of the request (user)
def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

# Fetches the location of the user based on the ip address
def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data
