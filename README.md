# REE - Railway Energy Explorer

## Overview

The Railway Energy Explorer (REE) is an interactive web application that analyzes and visualizes the potential for piezoelectric energy harvesting from Austrian railway infrastructure. This project combines geospatial data analysis, machine learning insights, and interactive visualization to identify optimal locations for renewable energy generation along train routes.

### Project Goals

- **Analyze Austrian railway network** for energy harvesting potential
- **Visualize train routes** with interactive maps showing energy potential indicators
- **Provide AI-powered insights** through an integrated chatbot assistant
- **Identify high-potential segments** for piezoelectric energy harvesting installations

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [API Documentation](#api-documentation)
- [Docker Configuration](#docker-configuration)
- [Development](#development)

## Features

### Interactive Map Visualization
- **Real-time route visualization** of Austrian train network
- **Color-coded route types**: S-Bahn, Regional, Intercity, Long-distance
- **Interactive markers** showing train stops with detailed information
- **Highlighted energy potential segments** with green indicators
- **Customizable filters** for route selection and data sampling

### AI-Powered Chatbot
- **Natural language queries** about the dataset and analysis
- **Context-aware responses** using Ollama's LLaMA models
- **Dual dataset awareness**: Complete dataset vs. currently filtered data
- **Real-time statistics** and insights generation

### Data Analysis Features
- **Energy Potential Index (EPI)** calculation and visualization
- **Route-specific analysis** with filtering capabilities
- **Statistical summaries** of energy harvesting potential
- **Exportable results** in CSV format

### Technical Features
- **Responsive design** with wide-screen layout optimization
- **Docker containerization** for easy deployment
- **Real-time data filtering** and processing
- **Scalable architecture** supporting large datasets

## Technologies Used

### Backend & Data Processing
- **Python 3.13** - Core programming language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations

### Frontend & Visualization
- **Streamlit** - Web application framework
- **Folium** - Interactive map generation
- **streamlit-folium** - Streamlit-Folium integration

### AI & Machine Learning
- **Ollama** - Local LLM inference
- **LLaMA 3.2** - Language model for chatbot responses

### Deployment & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration

### Data Sources
- **GTFS (General Transit Feed Specification)** - Austrian railway data
- **ÖBB Open Data** - Austrian Federal Railways dataset

## Project Structure

```
REE/
├── APP/                                    # Main application directory
│   ├── app.py                             # Main Streamlit application
│   ├── chatbot_page.py                    # AI chatbot functionality
│   ├── streamlit_app.py                   # Multi-page app router
│   ├── Dockerfile                         # App container configuration
│   └── requirements.txt                   # Python dependencies
├── data/                                   # Dataset directory
│   └── oebb_gtfs/                         # Austrian railway GTFS data
│       ├── stop_times_geo_with_startEnd_calc.csv  # Main processed dataset
│       ├── routes.txt                     # Route information
│       ├── stops.txt                      # Station/stop information
│       ├── trips.txt                      # Trip schedules
│       ├── train_energy_potential_austria.csv     # Energy potential analysis
│       └── [other GTFS files...]         # Additional transit data
├── docker-compose.yml                     # Multi-service deployment config
├── Dockercompose.yml                      # Alternative compose file
└── README.md                              # This documentation
```

## Installation

### Prerequisites

- **Docker** and **Docker Compose** installed
- **git lfs** installed
- **Git** for cloning the repository
- **4GB+ RAM** recommended for Ollama models

### Quick Start with Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/MarcelDS24/REE.git
cd REE
```

2. **Download the dataset**
```bash
#If the dataset is not included via git lfs, download it manually:
# Download data from Google Drive
# https://drive.google.com/drive/folders/1JSCW--szNNXOfGwqpuQLYxh_6nVby1OB
# Extract to ./data/oebb_gtfs/ directory

```


3. **Install and setup Ollama agent**
```bash
# macOS
brew install ollama

# Start Ollama server
ollama serve

# Pull required models
ollama pull llama3.2
```
3. **Start the application using Docker Compose**
```bash
docker compose up --build
```

4. **Access the application**
- **Streamlit App**: http://localhost:8501
- **Ollama API**: http://localhost:11434

### Manual Installation

1. **Install Python dependencies**
```bash
cd APP
pip install -r requirements.txt
```

2. **Install and setup Ollama**
```bash
# macOS
brew install ollama

# Start Ollama server
ollama serve

# Pull required models
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

3. **Run the application**
```bash
#MAKE SURE THE DATA DIRECTORY IS CORRECT IN Streamlit_app.py
streamlit run streamlit_app.py
```

## Usage

### Main Interface

1. **Map Visualization**
   - Use the sidebar to adjust visualization parameters
   - Select specific routes or view all Austrian routes
   - Toggle markers, labels, and energy potential highlighting
   - Adjust map height for optimal viewing

2. **Energy Potential Analysis**
   - Enable "Highlight highest-speed segment" to see energy harvesting candidates
   - Green highlighted segments indicate high energy potential
   - Download highlighted segments data as CSV

3. **AI Chatbot Assistant**
   - Ask questions about the dataset in natural language
   - Examples:
     - "What's the highest EPI value?"
     - "Which route has the best energy potential?"
     - "How many stations are in the current view?"
     - "Compare the complete dataset to what's currently shown"

### Configuration Options

#### Sidebar Controls
- **Sample Size**: Limit data for performance (0 = all data)
- **Route Selection**: Focus on specific railway routes
- **Visualization Options**: Toggle markers, labels, highlights
- **Map Settings**: Adjust height and view area

#### Data Filtering
- **Austria-only view**: Filter to Austrian territory
- **Route-specific analysis**: Select individual routes
- **Performance optimization**: Sample data for large datasets

## Data Sources

### Primary Dataset
- **Source**: Austrian Federal Railways (ÖBB) GTFS Data
- **Format**: CSV files following GTFS specification
- **Coverage**: Complete Austrian railway network
- **Update Frequency**: Periodic updates from ÖBB Open Data

### Key Data Files
- `stop_times_geo_with_startEnd_calc.csv` - Main processed dataset with EPI calculations
- `routes.txt` - Railway route definitions
- `stops.txt` - Station and stop information
- `trips.txt` - Scheduled trip information
- `train_energy_potential_austria.csv` - Energy potential analysis results

### Data Processing
- **Geospatial enrichment** with latitude/longitude coordinates
- **Energy Potential Index (EPI)** calculation based on traffic and speed
- **Route categorization** (S-Bahn, Regional, Intercity, etc.)
- **Performance metrics** for energy harvesting assessment

## API Documentation

### Chatbot Integration

The application integrates with Ollama for AI-powered responses:

```python
# Model Selection (in order of preference)
models = ["llama3.2:1b", "llama3.2:3b", "llama3.2"]

# Context provided to AI
context = {
    "complete_dataset": "Full Austrian railway network",
    "filtered_dataset": "Currently displayed data",
    "epi_metrics": "Energy Potential Index statistics",
    "route_information": "Selected routes and segments"
}
```

### Environment Variables

```bash
OLLAMA_HOST=http://localhost:11434  # Ollama server URL
```

## Docker Configuration

### Services

1. **Ollama Service**
   - Provides local LLM inference
   - Automatically pulls required models
   - Health checks for service reliability

2. **Streamlit App**
   - Main web application
   - Connects to Ollama for AI features
   - Volume-mounted data directory

### Docker Compose

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    
  app:
    build: ./APP
    ports:
      - "8501:8501"
    depends_on:
      - ollama
    environment:
      OLLAMA_HOST: http://ollama:11434
```

## Development

### Adding New Features

1. **Map Visualizations**: Modify `app.py` Folium configuration
2. **Data Processing**: Update pandas operations in data loading section
3. **AI Responses**: Enhance chatbot prompts in `chatbot_page.py`
4. **UI Components**: Add Streamlit widgets and layouts

### Performance Optimization

- Use data sampling for large datasets
- Implement caching for repeated operations
- Optimize Folium map rendering
- Consider data preprocessing for better performance

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add docstrings for new functions
- Update README for significant changes
- Test with Docker before submitting

