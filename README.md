# YelpCamp AI MCP

## System Architecture

The YelpCamp AI MCP system follows a modern microservices architecture with the following key components:

1. **Frontend Interface**: Web-based UI for user interaction
2. **FastAPI Backend**: Core application logic and API endpoints
3. **Gemini AI Service**: Natural language processing and recommendation engine
4. **Database**: Stores campground information and user data
5. **Docker Container**: Encapsulates the application for consistent deployment
6. **Render Cloud**: Hosting platform for the deployed application

### Example Interaction Flow

1. User types "Find me a campground near Yellowstone with lake access" in the chat interface
2. Frontend sends request to FastAPI backend
3. Backend processes request and sends to Gemini AI service
4. Gemini AI analyzes query and generates recommendations
5. Backend formats recommendations and sends back to frontend
6. Frontend displays results to user with map view and details

### Technical Stack

- **Backend**: Python 3.9+ with FastAPI framework
- **AI Processing**: Gemini API for natural language understanding
- **Database**: PostgreSQL for relational data storage
- **Containerization**: Docker for consistent deployment
- **Hosting**: Render cloud platform

### Deployment Architecture

```mermaid
flowchart TD
    A[GitHub Repository] -->|Source Code| B[Docker Build]
    B -->|Container Image| C[Render Cloud]
    C -->|Hosted Application| D[Users]
    E[CI/CD Pipeline] -->|Automated Deployments| C
```

For a more detailed view of the architecture, see the [flowchart.md](flowchart.md) file.

```mermaid
flowchart TD
    A[User] -->|Queries| B[Frontend Interface]
    B -->|API Requests| C[FastAPI Backend]
    C -->|Gemini API Requests| D[Gemini AI Service]
    D -->|Responses| C
    C -->|Recommendations| B
    B -->|Display Results| A
    
    C -->|Data Storage| E[Database]
    E -->|Campground Data| C
    
    F[Docker Container] -->|Runs| C
    G[Render Cloud] -->|Hosts| F
    
    H[GitHub Repository] -->|Source Code| F
    H -->|CI/CD Pipeline| G
```

For a more detailed view of the architecture, see the [flowchart.md](flowchart.md) file.

[![Docker Pulls](https://img.shields.io/docker/pulls/shresthshukla/yelpcamp-mcp-ai)](https://hub.docker.com/r/shresthshukla/yelpcamp-mcp-ai)
[![Render Deployment](https://img.shields.io/badge/Deployed%20on-Render-blue)](https://yelpcamp-mcp-ai.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-orange)](https://gemini.google.com/)

## Overview

YelpCamp AI MCP is an advanced AI-powered chatbot for YelpCamp, providing intelligent recommendations and assistance for campgrounds. This application leverages FastAPI for the backend, Gemini AI for natural language processing, and is containerized with Docker for easy deployment.

![Architecture Diagram](screenshots/architecture_diagram.png)

## Features

- Intelligent campground recommendations
- Natural language processing for user queries
- FastAPI backend for robust API endpoints
- Docker containerization for easy deployment
- Render cloud deployment

## Screenshots

![Chat Interface](screenshots/chat_interface.png)
![Recommendation Example](screenshots/recommendation_example.png)

## Getting Started

### Prerequisites

- Docker installed on your machine
- Python 3.9 or higher
- A Gemini API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yelpcamp-ai-mcp.git
   cd yelpcamp-ai-mcp
   ```

2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Set `GEMINI_API_KEY` in your `.env` file.

### Running Locally

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

### Docker Setup

1. Pull the Docker image:
   ```bash
   docker pull shresthshukla/yelpcamp-mcp-ai
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key shresthshukla/yelpcamp-mcp-ai
   ```

### Render Deployment

The application is deployed on Render at [https://yelpcamp-mcp-ai.onrender.com](https://yelpcamp-mcp-ai.onrender.com).

## API Documentation

For detailed API documentation, visit the Swagger UI when running locally:

[http://localhost:8000/docs](http://localhost:8000/docs)

## Testing

Run all tests:
```bash
uv run python -m pytest
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact [your.email@example.com](mailto:your.email@example.com).

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Gemini AI](https://gemini.google.com/)
- [Docker](https://www.docker.com/)
- [Render](https://render.com/)
