# Multimodal AI Design Analysis Suite

A cutting-edge AI-powered design analysis platform that leverages multiple specialized agents to provide comprehensive design feedback, market intelligence, and actionable improvements for UI/UX designs.

## 🚀 Features

- **Multi-Agent Architecture**: Five specialized AI agents for comprehensive analysis
- **Real-time Streaming**: Server-sent events for live analysis updates  
- **Advanced Image Processing**: CLIP embeddings and computer vision analysis
- **OpenRouter Integration**: Access to multiple LLM models through unified API
- **Vector Database**: ChromaDB for semantic similarity and design patterns
- **Production Ready**: Docker containers, monitoring, and scalability

## 🏗️ Architecture

### Backend (FastAPI + LangGraph)
- **FastAPI**: High-performance async API server
- **LangGraph**: Agent orchestration and workflow management  
- **OpenRouter**: Unified LLM gateway (GPT-4V, Claude-3.5, CodeLlama)
- **ChromaDB**: Vector database for embeddings
- **CLIP**: Vision-language model for image understanding

### Frontend (React + Next.js)
- **Next.js**: React framework with server-side rendering
- **Material-UI**: Modern component library
- **TypeScript**: Type-safe development
- **Real-time Updates**: Server-sent events integration

### AI Agents
1. **Visual Analysis Agent**: Color, typography, layout, visual hierarchy
2. **UX Critique Agent**: Usability heuristics, accessibility, user journey
3. **Market Research Agent**: Competitive analysis, trends, positioning  
4. **Technical Feasibility Agent**: Implementation complexity, technology stack
5. **Brand Alignment Agent**: Brand consistency, identity strength

## 🛠️ Installation

### Prerequisites
- Docker and Docker Compose
- OpenRouter API key ([Get one here](https://openrouter.ai))
- 8GB+ RAM recommended for AI models

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multimodal-ai-design-analysis-suite
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Metrics: http://localhost:9090

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development  
```bash
cd frontend
npm install
npm run dev
```

## 📊 Usage

1. **Upload Design**: Drag & drop or select an image file (PNG, JPG, etc.)
2. **Configure Analysis**: Set user preferences and brand guidelines
3. **Run Analysis**: Watch real-time progress as AI agents analyze your design
4. **Review Results**: Get comprehensive insights and actionable recommendations

### Supported Image Formats
- JPG, JPEG, PNG, GIF, BMP, WebP
- Maximum file size: 10MB
- Recommended resolution: 1280x720 or higher

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `CHROMA_PERSIST_DIRECTORY` | Vector database storage path | `./chroma_db` |
| `MAX_IMAGE_SIZE` | Maximum image upload size | `10485760` (10MB) |
| `RATE_LIMIT_CALLS` | API rate limit per window | `100` |
| `RATE_LIMIT_PERIOD` | Rate limit time window (seconds) | `60` |

### Model Configuration

The system uses these models by default:
- **Vision**: `openai/gpt-4-vision-preview`
- **Text**: `anthropic/claude-3-5-sonnet-20241022`  
- **Code**: `meta-llama/codellama-34b-instruct`

You can configure different models in `backend/app/core/config.py`.

## 🚀 Deployment

### Production Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Update with production values
   ```

2. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Set up monitoring**
   - Prometheus metrics at `/metrics`
   - Health checks at `/health`
   - Grafana dashboards available

### Scaling Considerations

- **Horizontal Scaling**: Load balance multiple backend instances
- **GPU Support**: Add GPU support for faster image processing
- **Caching**: Implement Redis caching for frequently analyzed designs
- **CDN**: Use CDN for static assets and image delivery

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests  
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📖 API Documentation

### Main Endpoints

- `POST /api/v1/analyze` - Submit design for analysis
- `GET /api/v1/analysis/{id}/status` - Get analysis status  
- `GET /api/v1/analysis/{id}/report` - Get complete report
- `GET /api/v1/models` - List available AI models
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### WebSocket Events

The analysis endpoint streams events:
- `status` - Analysis status updates
- `progress` - Progress percentage (0-100)
- `result` - Individual agent results
- `complete` - Final analysis complete
- `error` - Error notifications

## 🔒 Security

- **Rate Limiting**: API endpoints are rate-limited
- **Input Validation**: All uploads and inputs validated
- **CORS**: Configurable CORS policies  
- **Security Headers**: Standard security headers applied
- **Container Security**: Non-root user in containers

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Standards

- **Code Style**: Follow PEP 8 (Python), ESLint (JavaScript)
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update docs for new features
- **Type Safety**: Use TypeScript for frontend, type hints for Python

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- OpenRouter for unified LLM access
- OpenAI for CLIP vision models
- LangChain team for LangGraph framework
- Material-UI for React components
- ChromaDB for vector database

---

**Built with ❤️ for designers and developers**
