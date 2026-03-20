# 
# # LLM retail analysis
# 
# This project illustrates a simple example of enabling less technical users to write data queries in natural language, which an LLM converts to SQl to run against a database.
# This was produced for my own learning purposes and is not intended as production ready code.
# 
# ---
# 
# ### Notebook Information
# * **Author:** Stuart Rothwell
# * **Date:** 19 March 2026
# * **Status:** In-Progress / Exploration
# * **Data:** Hugging Face RetailLLM/store_data dataset: `https://huggingface.co/datasets/RetailLLM/store_data`
# 
# ### Environment Requirements
# * **Python Version:** 3.12.12
# * **Key Libraries:** `os`, `json`, `openai`, `gradio`, `datasets`, `sqlite3`
# 
# ### Table of Contents
# 1. Set up (imports & initialisation)
# 3. Import data
# 4. Function definitions
# 5. Instantiate UI



#Imports

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from datasets import load_dataset
import sqlite3
import pandas as pd


# Initialization

load_dotenv(override=True)

hf_url = "https://router.huggingface.co/v1"
hf_api_key = os.getenv('HF_TOKEN')
if hf_api_key:
    print(f"Hugging Face API Key exists")
else:
    print("Hugging Face API Key not set")
    
MODEL = "openai/gpt-oss-20b"

openai = OpenAI(api_key=hf_api_key, base_url=hf_url)

    

# Data
dataset = load_dataset("RetailLLM/store_data", split="train").to_pandas()

df_formatted = dataset.copy()
df_formatted.rename(columns={'Uniq Id':'Unique_id', 
                            'Crawl Timestamp':'Timestamp', 
                            'Product Title':'Product_Title',
                            'Product Description': 'Product_Description',
                            'Pack Size Or Quantity':'Pack_Size_Qty',
                            'Site Name':'Site_Name',
                            'Combo Offers':'Combo_Offers',
                            'Stock Availibility':'Stock_Availability',
                            'Product Asin':'Product_Asin',
                            'Image Urls':'Image_Urls'}, inplace=True)
df_formatted = df_formatted[~df_formatted['Mrp'].str.startswith('.', na=False)]
df_formatted = df_formatted[~df_formatted['Price'].str.startswith('.', na=False)]
df_formatted['Mrp'] = df_formatted['Mrp'].astype(float)
df_formatted['Price'] = df_formatted['Price'].astype(float)



# Set up sqlite database
DB = "retail_products.db"
conn = sqlite3.connect(DB)
df_formatted.to_sql("products", conn, if_exists="replace", index=False)
conn.close()

# Get the DB schema, to insert into LLM prompt
def get_schema():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schema=f""
    for table in tables:
        print(table, flush=True)
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        
        for col in columns:
            # col format: (id, name, type, notnull, default_value, pk)
            schema += f"\nTable: {table} | Column: {col[1]} | Type: {col[2]} | Primary Key: {bool(col[5])}"

    conn.close()
    return schema

schema = get_schema()



# Function to execute sql query against the database
def execute_sql_query(query):
    forbidden_words = ["DELETE", "UPDATE", "DROP", "ALTER", "TRUNCATE"]
    print(f"DATABASE TOOL CALLED: execute_sql_query, with query:\n {query}", flush=True)
    forbidden_matches = [word for word in query.upper().split() if word in forbidden_words]
    if len(forbidden_matches)>0:
        result = f"SQL query cannot be run because it contains forbidden words: {forbidden_matches}"
        print(result, flush=True)
    else:
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute(f'{query}')
            result = cursor.fetchall()
    flattened = "".join(map(str, result))

    return result, flattened

# Put function into dictionary structure required for LLM:
query_function = {
    "name": "execute_sql_query",
    "description": "Execute a query against the sql db",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to execute",
            },
        },
        "required": ["query"],
        "additionalProperties": False
    }
}

# List tools:
tools = [{"type": "function", "function": query_function}]


# Chat function
def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

         # Debugging
        for message in messages:
            print(message)

        response = openai.chat.completions.create(model=MODEL, messages=messages)
    
    return response.choices[0].message.content

# Handle tools function
def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "execute_sql_query":
            arguments = json.loads(tool_call.function.arguments)
            query = arguments.get('query')
            query_results, query_results_flattened = execute_sql_query(query)
            responses.append({
                "role": "tool",
                "content": query_results_flattened,
                "tool_call_id": tool_call.id
            })
    return responses

# System prompt

system_message = f"""
You are a data analyst. You take instructions from a business user, interpret these into SQL code, and then use tools to run the SQL code against a database.
The database has the following tables, columns and data types:
{schema}
"""



# Call UI
gr.ChatInterface(fn=chat, type="messages").launch()

# ### TO DO
# 
#-  Make readme.md
# - Push to Git



