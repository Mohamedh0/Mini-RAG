# Mini-RAG

This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.8 or later

#### Install Python & uv

1- Download Python from [here](https://www.python.org/)

2- Download uv package manager using the following command via WSL :
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3- Create a new environment using the following command:
```bash
uv venv .venv
```

4- Activate the environment:
```bash
source .venv/bin/activate
```

### (Optional) Setup you command line interface for better readability
```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages
```bash
uv sync
```

### Setup the environment variables
```bash
cp .env.example .env
```

Set your environment variables in the .env file. Like OPENAI_API_KEY value.

### Run the FastAPI server
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
