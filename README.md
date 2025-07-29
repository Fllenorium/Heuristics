# Heuristics AI

An AI-powered platform for testing business decisions on synthetic populations before implementing them in real life.

## 🚀 Features

- **AI Decision Analysis**: Use GPT-4 to analyze business decisions through the lens of behavioral economics
- **Synthetic Population Generation**: Create realistic populations with diverse demographics and behavioral traits
- **Behavior Simulation**: Predict how different types of people will react to your business decisions
- **Real-time Insights**: Get detailed analysis and actionable recommendations
- **Production Ready**: Built with Flask, includes caching, rate limiting, and error handling

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **AI**: OpenAI GPT-4 API
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Caching**: Redis (optional)
- **Rate Limiting**: Flask-Limiter
- **Logging**: Structured JSON logging

## 📦 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd heuristics-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.template .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   Visit `http://localhost:5000` to access the application.

## 🎯 Usage

### 1. Generate Population

Define your target population by setting:
- Demographics (age, income, location)
- Behavioral traits (tech savviness, price sensitivity)
- Population size (100-10,000 people)

### 2. Input Decision

Describe your business decision in plain English:
- "Increase our SaaS pricing by 30%"
- "Launch our product in European markets"
- "Change our brand colors from blue to green"
- "Require account creation before purchase"

### 3. Run Simulation

The AI will:
- Analyze your decision using behavioral economics principles
- Simulate individual reactions for each person in your population
- Aggregate results into population-level insights

### 4. Review Results

Get detailed insights including:
- Overall sentiment distribution
- Behavioral segments
- Predicted business outcomes
- Key insights and recommendations

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Homepage
- `GET /dashboard` - Simulation dashboard
- `GET /api/health` - Health check

### Simulation API

- `POST /api/analyze-decision` - Analyze a business decision
- `POST /api/generate-population` - Generate synthetic population
- `POST /api/run-simulation` - Run complete simulation

### Example API Usage

```python
import requests

# Analyze a decision
response = requests.post('http://localhost:5000/api/analyze-decision', json={
    'decision': 'Increase pricing by 20%',
    'parameters': {'type': 'pricing'}
})

# Generate population
response = requests.post('http://localhost:5000/api/generate-population', json={
    'size': 1000,
    'parameters': {
        'age_min': 18,
        'age_max': 65,
        'income_level': 'mixed',
        'region': 'us'
    }
})
```

## 🏗️ Architecture

```
heuristics-ai/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
├── src/
│   ├── models/          # Data models
│   │   └── population.py
│   ├── services/        # Core business logic
│   │   ├── decision_analyzer.py
│   │   └── behavior_engine.py
│   └── utils/           # Utility functions
│       └── logger.py
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
└── static/             # Static assets
    ├── css/
    └── js/
```

## 🧠 AI Prompt Engineering

The platform uses sophisticated prompt engineering to make GPT-4 think like a behavioral economist:

### Decision Analysis Prompts
- Considers cognitive biases (loss aversion, anchoring, etc.)
- Analyzes demographic segments and motivations
- Identifies psychological triggers
- Extracts measurable parameters

### Behavior Simulation Prompts
- Role-plays as specific individuals
- Considers personality traits and values
- Predicts authentic reactions
- Provides detailed reasoning

## 📊 Example Decisions

### Pricing Changes
```
"Increase our SaaS pricing by 30% for new customers starting next month"
```

### Product Updates
```
"Add a mandatory user onboarding tutorial that takes 5 minutes to complete"
```

### Marketing Strategy
```
"Switch from email marketing to TikTok advertising for our Gen Z products"
```

### Business Model
```
"Move from one-time purchase to subscription model with monthly billing"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `SECRET_KEY` | Flask secret key | Random |
| `FLASK_ENV` | Environment | development |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `MAX_POPULATION_SIZE` | Maximum population size | 10000 |
| `DEFAULT_BATCH_SIZE` | API batch size | 50 |
| `CACHE_TTL` | Cache time-to-live | 3600 |
| `LOG_LEVEL` | Logging level | INFO |

### Production Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Use a proper WSGI server (Gunicorn included)
3. Set up Redis for caching
4. Configure proper logging
5. Set strong secret keys

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔒 Security

- Rate limiting on API endpoints
- Input validation and sanitization
- Secure session management
- Environment variable protection
- Error handling without information leakage

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/
```

## 📈 Performance

- Caching system for repeated requests
- Batch processing for large populations
- Rate limiting to respect OpenAI API limits
- Efficient database queries
- Optimized frontend loading

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] A/B testing framework
- [ ] Advanced demographic filters
- [ ] Historical decision tracking
- [ ] Integration with business intelligence tools
- [ ] Multi-language support
- [ ] Advanced visualization dashboards
