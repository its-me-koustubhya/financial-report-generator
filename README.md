# 📊 Business Report Generator

An intelligent multi-agent system that generates comprehensive financial analysis reports using LangGraph and AI agents.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for data collection, analysis, writing, and editing
- **Intelligent Quality Checks**: Validates data quality and retries when needed
- **Early Exit Strategy**: Efficiently handles cases with insufficient data
- **Conditional Routing**: Smart workflow that adapts based on data quality
- **Automated Report Generation**: Creates professional markdown reports
- **CLI Interface**: Easy-to-use command-line interface

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Collector │ → Searches web, collects financial data
└────────┬────────┘
         ↓
┌─────────────────┐
│    Analyst      │ → Extracts metrics, identifies trends
└────────┬────────┘
         ↓
  [Quality Check] → Validates data quality
         ↓
┌─────────────────┐
│     Writer      │ → Generates structured report
└────────┬────────┘
         ↓
┌─────────────────┐
│     Editor      │ → Polishes and formats
└────────┬────────┘
         ↓
  [Quality Check] → Validates report quality
         ↓
    [Final Report]
```

## 🚀 Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:

```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
MODEL_NAME=llama-3.3-70b-versatile
```

## 📖 Usage

### Basic Usage

```bash
python main.py "Tesla"
```

### With Specific Focus

```bash
python main.py "Apple Inc" --focus "Q4 2024 earnings"
```

### Custom Output Directory

```bash
python main.py "Microsoft" --output reports/
```

### Display Only (Don't Save)

```bash
python main.py "Amazon" --no-save
```

### Quiet Mode

```bash
python main.py "Google" --quiet
```

## 📁 Project Structure

```
business_report_generator/
├── agents/              # Agent implementations
│   ├── data_collector.py
│   ├── analyst.py
│   ├── writer.py
│   ├── editor.py
│   └── quality_checker.py
├── graph/              # LangGraph workflow
│   ├── state.py
│   └── workflow.py
├── tools/              # Utility functions
├── output/             # Generated reports
├── config.py           # Configuration
├── main.py            # CLI entry point
└── README.md
```

## 🎯 Agents

### 1. Data Collector Agent

- Generates intelligent search queries
- Collects financial data from multiple sources
- Validates data relevance

### 2. Analyst Agent

- Extracts financial metrics (revenue, profit, growth)
- Identifies key insights and trends
- Structures findings for reporting

### 3. Writer Agent

- Creates comprehensive report sections
- Maintains professional business tone
- Incorporates data and analysis

### 4. Editor Agent

- Polishes grammar and formatting
- Ensures consistency and readability
- Adds metadata and structure

### 5. Quality Checker

- Validates data and report quality
- Triggers retries when needed
- Implements early exit for insufficient data

## 🔧 Configuration

Edit `config.py` to customize:

- LLM models and temperatures
- Search parameters
- Quality thresholds
- Report formats

## 📊 Output

Reports are saved as markdown files in the `output/` directory:

```
output/
├── Tesla_report_20241118_143022.md
├── Apple_Inc_report_20241118_144533.md
└── ...
```

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 🙏 Acknowledgments

Built with:

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [Groq](https://groq.com/)
- [Tavily](https://tavily.com/)
