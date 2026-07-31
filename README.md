# Agentic Task Assistant

A lightweight Agentic AI Assistant built from scratch using the ReAct (Reason + Act) pattern. Instead of generating answers in a single LLM call, the agent performs iterative reasoning, decides when external information is required, invokes the appropriate tool, observes the result, and continues until it reaches a final answer.

This project demonstrates the core concepts behind modern LLM-powered AI agents, including planning, tool calling, response parsing, and evaluation.

## Features

🧠 ReAct (Thought → Action → Observation → Final Answer) reasoning loop
🔧 Dynamic tool selection
🌐 Web Search integration
📚 Wikipedia lookup
🧮 Safe AST-based calculator (no unsafe eval())
📅 Current date & time tool
💬 Interactive Streamlit interface with live reasoning trace
📊 Evaluation suite for benchmarking agent performance
⚡ Free Groq API support (Llama 3)
🔄 Modular tool registry for easily adding new tools
📸 Demo

## Live Reasoning Trace 

docs/demo.gif

## Evaluation Results

docs/evaluation.png

## 🏗️ Architecture
                 User Query
                      │
                      ▼
          ┌─────────────────────┐
          │     ReAct Agent     │
          │  Thought Generation │
          └──────────┬──────────┘
                     │
             Action + Input
                     ▼
          ┌─────────────────────┐
          │    Tool Registry    │
          ├─────────────────────┤
          │ Web Search          │
          │ Wikipedia           │
          │ Calculator          │
          │ Date & Time         │
          └──────────┬──────────┘
                     │
               Observation
                     ▼
          Continue ReAct Loop
                     │
                     ▼
              Final Response
              
## 📂 Project Structure
agentic-task-assistant/
│
├── app.py
├── requirements.txt
├── .env.example
│
├── agent/
│   ├── core.py
│   ├── prompts.py
│   ├── parser.py
│   ├── tools.py
│   └── llm.py
│
├── eval/
│   ├── run_eval.py
│   ├── test_tasks.json
│   └── results.json
│
├── docs/
│   ├── screenshot.png
│   ├── demo.gif
│   └── architecture.png
│
└── README.md

## 🛠️ Tech Stack
Python
Streamlit
Groq API (Llama 3)
Anthropic Claude (optional)
Wikipedia API
DuckDuckGo Search
Python AST
python-dotenv

## 🚀 Installation

1. Clone the repository

git clone https://github.com/<username>/agentic-task-assistant.git
cd agentic-task-assistant

2. Create a virtual environment

python3 -m venv venv

3. Activate it

- macOS/Linux

source venv/bin/activate

- Windows

venv\Scripts\activate

4. Install dependencies

pip install -r requirements.txt

5. Create a .env file

GROQ_API_KEY=your_api_key_here

6. Run the application

streamlit run app.py

7. Open your browser at

http://localhost:8501

## 📊 Evaluation

Run the evaluation suite

python eval/run_eval.py

The evaluation reports:

Tool selection accuracy
Latency
Token usage
API cost
Success rate

## 🎯 Design Decisions

1. Why ReAct?

Instead of directly answering every question, the agent reasons step-by-step, determines whether external information is needed, invokes the appropriate tool, and continues reasoning until it reaches a reliable answer.

2. Why a Tool Registry?

A modular registry makes it easy to add, remove, or extend tools without changing the core reasoning loop.

3. Why an AST-Based Calculator?

Using Python's eval() can execute arbitrary code. This project uses a restricted AST parser that safely supports only arithmetic operations.

4. Why a Maximum Step Limit?

Bounding the reasoning loop prevents infinite iterations, reduces API costs, and improves reliability.

## 🔮 Future Improvements
Conversation memory
Code execution tool
PDF question answering
Retrieval-Augmented Generation (RAG)
SQL database tool
Multi-agent collaboration
Vector database integration
Cost analytics dashboard
Docker support

## 💡 Skills Demonstrated
Agentic AI
Large Language Models (LLMs)
ReAct Framework
Prompt Engineering
Tool Calling
API Integration
Software Architecture
Python Development
AI Evaluation
Streamlit
