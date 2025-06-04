# Agentic AI

Agentic AI is a project focused on building autonomous, agent-based Question Generator.

## Features

- Modular agent architecture
- Task planning and execution
- Extensible plugin system
- Easy integration with external APIs

## Getting Started

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/agentic_ai.git
    cd agentic_ai
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the main application (uvicorn):**
    ```bash
    uvicorn main:app --reload
    ```

## Configuration

Create an `api_key.env` file in the project root with your API keys:

```
GROQ_API_KEY = "your-groq-key"
TAVILY_API_KEY = "your-tavily-key"
```

### Allowed Topics

- Probability
- Statistics
- Linear Algebra
- Vector 3D
- Basic C programming
- Basic Python programming
- Matrix
- Determinant

## Usage

Edits to the Prompt and Topic Whitelist can be made in services/generator.py

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.