# 🤖 Agentic Task Assistant

A lightweight **Agentic AI Assistant** built from scratch using the **ReAct (Reason + Act)** pattern. Instead of generating answers in a single LLM call, the agent performs iterative reasoning, decides when external information is required, invokes the appropriate tool, observes the result, and continues until it reaches a final answer.

This project demonstrates the core concepts behind modern **LLM-powered AI agents**, including planning, tool calling, response parsing, and evaluation.

---

## ✨ Features

- 🧠 ReAct (Thought → Action → Observation → Final Answer) reasoning loop
- 🔧 Dynamic tool selection
- 🌐 Web Search integration
- 📚 Wikipedia lookup
- 🧮 Safe AST-based calculator (AST-based, no unsafe `eval()`)
- 📅 Current Date & Time tool
- 💬 Interactive Streamlit interface with live reasoning trace
- 📊 Evaluation suite for benchmarking agent performance
- ⚡ Free Groq API support (Llama 3)
- 🔄 Modular tool registry for easily adding new tools

---

## 📸 Demo

### Live Reasoning Trace

![Demo](docs/demo.gif)

### Evaluation Results

![Evaluation](docs/evaluation.png)

---

## 🏗️ Architecture

```text
                 User Query
                      │
                      ▼
          ┌─────────────────────┐
          │     ReAct Agent     │
          │ Thought Generation  │
          └──────────┬──────────┘
                     │
             Action + Input
                     ▼
          ┌─────────────────────┐
          │    Tool Registry    │
          ├─────────────────────┤
          │ • Web Search        │
          │ • Wikipedia         │
          │ • Calculator        │
          │ • Date & Time       │
          └──────────┬──────────┘
                     │
               Observation
                     ▼
            Continue ReAct Loop
                     │
                     ▼
              Final Response
```

---

## 📂 Project Structure

```text
agentic-task-assistant/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
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
└── docs/
    ├── architecture.png
    ├── demo.gif
    └── evaluation.png
```

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq API (Llama 3)
- Anthropic Claude (optional)
- DuckDuckGo Search
- Wikipedia API
- python-dotenv
- Python AST

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Moulya-Reddy/Agentic_Task_Assistant.git

cd Agentic_Task_Assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the environment

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

```env
GROQ_API_KEY=your_api_key_here
```

### 6. Run the application

```bash
streamlit run app.py
```

Open your browser and visit

```
http://localhost:8501
```

---

## 📊 Evaluation

Run the evaluation suite using

```bash
python eval/run_eval.py
```

The evaluation reports:

- Tool selection accuracy
- Latency
- Token usage
- API cost
- Success rate

---

## 🎯 Design Decisions

### Why ReAct?

Instead of directly answering every question, the agent reasons step-by-step, determines whether external information is needed, invokes the appropriate tool, and continues reasoning until it reaches a reliable answer.

### Why a Tool Registry?

The modular registry allows new tools to be added without modifying the core reasoning loop.

### Why an AST-Based Calculator?

Using Python's `eval()` introduces security risks. This project uses a restricted AST parser that safely supports only arithmetic operations.

### Why a Maximum Step Limit?

Bounding the reasoning loop prevents infinite iterations, reduces API costs, and improves reliability.

---

## 🔮 Future Improvements

- Conversation memory
- Code execution tool
- PDF Question Answering
- Retrieval-Augmented Generation (RAG)
- SQL Database tool
- Multi-Agent collaboration
- Vector Database integration
- Cost analytics dashboard
- Docker deployment

---

## 💡 Skills Demonstrated

- Agentic AI
- Large Language Models (LLMs)
- ReAct Framework
- Prompt Engineering
- Tool Calling
- API Integration
- Python Development
- Software Architecture
- AI Evaluation
- Streamlit

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Moulya Reddy Kandhala**

GitHub: https://github.com/Moulya-Reddy
