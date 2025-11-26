
# TrendSpotter
A social media analytics tool that analyzes Twitter data to detect emerging trends 
and popular topics. Uses NLP and embeddings to identify key patterns, rank topics by frequency, engagement,
and location, providing actionable insights in real time.

---

## Description

TrendSpotter is a multi-agent, AI-driven platform designed to analyze social media data - particularly from 
Twitter and uncover emerging trends.
By combining Natural Language Processing (NLP), semantic embeddings, and multi-agent reasoning, the system 
evaluates engagement patterns, detects trending topics, and answers user queries through a coordinated team of
intelligent agents.

The platform’s architecture allows it to reason dynamically: each agent focuses on a specific analytical domain 
(such as trends, engagement, or general insights), while a central Orchestrator Agent merges their outputs to form
a complete, context-aware response.

---

## Features

- Collects and analyzes live Twitter data
- Cleans and normalizes textual input for NLP analysis
- Generates embeddings to detect semantic similarity between posts
- Detects emerging trends and ranks them by frequency and engagement
- Analyzes engagement metrics such as likes, shares, and retweets
- Provides location- and sentiment-specific trend insights
- Multi-agent system with coordinated reasoning
- Modular, extensible, and easy to integrate into larger analytics pipelines

---

## Project Structure
```bash
TrendSpotter/
│
├── frontend/
├── backend/
│   ├── main.py                                   # Entry point of the backend
│   ├── src/
│   │   ├── NLP/                                  # NLP utilities and Gemini API interface
            └── gemini_api.py
│   │   ├── agents/                               # Agents for data collection, processing, and answering
            ├── general_agent/                    # Handles general, non-domain-specific questions
                ├── general_agent.py
            ├── likes_agent/                      # Focuses on engagement-related insights (likes, reactions, shares)
                ├── likes_agent.py
            ├── orchestrator_agent/               # Central coordinator that delegates and merges agent responses
                ├── orchestrator_agent.py  
            └── trend_agent/
                ├── Answer_agent.py              # Generates answers about specific trends
                ├── Data_agent.py                # Manages and stores collected trend data
                ├── Input_processing_agent.py    # Cleans, filters, and preprocesses textual input
                └── trend_pipeline.py            # Full pipeline for trend detection and analysis
                
│   │   ├── collectors/                          # Modules for collecting raw data
            ├── prototype.py                     # Experimental data collection script
            └── twitter_client.py                # Connects to Twitter API and streams tweets
│   │   ├── processors/                          # Data cleaning and preprocessing modules
            ├── text_cleaner.py                  # Cleans text: removes emojis, punctuation, and URLs
            └── utils.py                         # Helper functions for cleaning, parsing, and formatting
│   │   └── analyzers/                           # Trend detection logic
            └── trend_detector.py                # Core algorithm for trend discovery using embeddings
│   ├── main.py
    └── credentials.py

├── keys/
├── README.md                                     # Project documentation
├── TrendSpotter.docx                             # Additional project notes
└── .gitignore                                    # Files to ignore in Git
```

---

## File Descriptions

**backend/**  
- **main.py** – Entry point of the project; initializes all agents and runs the pipeline for data collection, preprocessing, analysis, and generating answers.  

**src/**  

- **NLP/**  
  - **gemini_api.py** – Handles communication with the Gemini API; sends prompts, receives responses, and generates embeddings.  
  - **prompt_instructions.txt** – Contains pre-defined instructions for the AI to guide responses.  
  - **__init__.py** – Marks the directory as a Python package.  

- **agents/**  
  The system uses four specialized agents that collaborate under an orchestrator:

  - **General Agent (general_agent.py)** – Answers broad or generic questions, or provides summary information about trends.
  - **Likes Agent (likes_agent.py)** – Analyzes engagement metrics such as likes, shares, and reactions to rank topic popularity.
  - **Trend Agent (trend_agent/)** – Detects, processes, and analyzes trending topics, and generates topic-specific answers.  
  - **Orchestrator Agent (orchestrator_agent.py)** – Routes user queries to the relevant agents, merges their responses, and ensures coherent, unified answers.
 - **__init__.py** – Marks the agents folder as a package.  

- **analyzers/**  
  - **trend_detector.py** – Analyzes embeddings and processed data to detect trends and rank their popularity.  
  - **__init__.py** – Marks the analyzers folder as a package.  

- **collectors/**  
  - **twitter_client.py** – Handles Twitter API integration for live data collection.  
  - **prototype.py** – Prototype scripts for testing data collection pipelines.  
  - **mock_data.csv** – Example CSV file with sample tweets for testing.  
  - **__init__.py** – Marks the collectors folder as a package.  

- **processors/**  
  - **text_cleaner.py** – Cleans raw tweet text (removes punctuation, URLs, emojis, etc.).  
  - **utils.py** – Helper functions used by various processing modules.  
  - **clean_mock_data.csv** – Processed version of the mock data.  
  - **__init__.py** – Marks the processors folder as a package.  
  
- **chatbot.py** – Implements a chat interface to interact with users and provide answers on trending topics.



---

## Technologies & Tools
- **Languages:** Python 3.10+
- **Libraries:** pandas, numpy, requests, tweepy, scikit-learn
- **Concepts:** NLP, embeddings, cosine similarity, trend detection
- **Tools:** Git, GitHub, PyCharm, CLI
- **Practices:** Modular programming, OOP, clean code

---

## How It Works
1. **Data Collection:** Fetches raw data from Twitter using a collector agent.
2. **Data Cleaning:** Cleans and normalizes text for analysis.
3. **Embedding Generation:** Converts text into vector embeddings.
4. **Trend Detection:** Analyzes and ranks trending topics.
5. **Results:** Outputs the most popular trends and topic

---


## How to Run
1. Clone the repository:
```bash
git clone https://github.com/tamaraviv/TrendSpotter.git
cd TrendSpotter
```

2. Ask a question


