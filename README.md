
# TrendSpotter
A social media analytics tool that analyzes Twitter data to detect emerging trends and popular topics. Uses NLP and embeddings to identify key patterns, rank topics by frequency, engagement, and location, providing actionable insights in real time.


# TrendSpotter

---

## Description

TrendSpotter is an AI-driven platform designed to analyze social media data,
particularly Twitter, to identify emerging trends and popular topics. Using
natural language processing (NLP) and embeddings, the system ranks topics based
on frequency, engagement, and location. The goal is to provide insights into
social patterns and highlight trends in real time.

---

## Features

- Collects and processes data from Twitter
- Cleans and normalizes textual input
- Generates embeddings for textual data to measure similarity
- Detects trending topics and ranks them based on popularity and engagement
- Provides location-specific trend analysis
- Modular and extensible architecture for future integration

---

## Project Structure
```bash
TrendSpotter/
│
├── backend/
│   ├── main.py                     # Entry point of the backend
│   ├── src/
│   │   ├── NLP/                    # NLP utilities and Gemini API interface
│   │   ├── agents/                 # Agents for data collection, processing, and answering
│   │   ├── collectors/             # Modules for collecting raw data
│   │   ├── processors/             # Data cleaning and preprocessing modules
│   │   └── analyzers/              # Trend detection logic
│
├── README.md                        # Project documentation
├── TrendSpotter.docx                # Additional project notes
└── .gitignore                       # Files to ignore in Git
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
  - **Answer_agent.py** – Processes questions about trends and generates answers using collected and processed data.  
  - **Data_agent.py** – Stores and manages collected data; serves as a knowledge base for other agents.  
  - **Input_processing_agent.py** – Handles initial input processing; cleans, filters, and prepares text for NLP analysis.  
  - **Pipeline.py** – Orchestrates the workflow: collection → processing → analysis → answer generation.  
  - **chatbot.py** – Implements a chat interface to interact with users and provide answers on trending topics.  
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
