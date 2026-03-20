# LLM Retail Analysis: Natural Language to SQL

A Python-based exploration into bridging the gap between non-technical users and structured data. This project leverages Large Language Models (LLMs) to convert natural language questions into executable SQL queries against a retail database.

> [!NOTE]  
> **Status:** In-Progress / Exploration  
> This project was created for personal learning purposes and is not intended for production environments.

---

## 🚀 How it Works
1. **Data Ingestion:** Loads the [`RetailLLM/store_data`](https://huggingface.co/datasets/RetailLLM/store_data) dataset from Hugging Face.
2. **Database Setup:** Cleans the data and migrates it into a local SQLite database.
3. **Schema Injection:** Dynamically extracts the DB schema and feeds it into the LLM's system prompt.
4. **Tool Use:** The LLM uses function calling to execute generated SQL queries safely.
5. **Interactive UI:** A Gradio-powered chat interface allows users to ask questions like *"What is the average price of products in stock?"*

---

## 🛠️ Environment Requirements
* **Python Version:** 3.12.12
* **Required Libraries:**
    * `openai`: For LLM orchestration.
    * `gradio`: For the web interface.
    * `datasets`: To pull the retail data.
    * `pandas` & `sqlite3`: For data manipulation and storage.
    * `python-dotenv`: To manage API credentials.

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rothwellstuart/llm-retail-analysis.git
cd llm-retail-analysis
```

### 2. Configure Environment Variables
Create a .env file in the root directory and add your API keys:
```bash
HF_TOKEN=your_hugging_face_token_here
```

### 3. Install Dependencies
```bash
pip install openai gradio datasets pandas python-dotenv
```

### 4. Run the Application
```bash
python your_script_name.py
```

##🔒 Security Features
To prevent accidental or malicious database modification, the execute_sql_query function includes a basic guardrail that blocks forbidden SQL keywords:
- DELETE, UPDATE, DROP, ALTER, TRUNCATE


### 👤 Author
Stuart Rothwell Date: 19 March 2026

### 📄 License
This project is open-source and available under the [MIT License](https://opensource.org/license/MIT).