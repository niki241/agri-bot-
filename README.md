# 🌾 Kisan Mitra — Agri Advisory Bot

**WhatsApp-first AI crop advisory for Indian farmers in Telugu & Hindi**

Kisan Mitra (కిసాన్ మిత్ర / किसान मित्र) helps small and marginal farmers get instant crop advisory via WhatsApp, powered by local AI (Ollama) with zero per-query cost.

---

## Features

- **WhatsApp Integration** — farmers text their crop problem, get AI advisory instantly
- **Telugu & Hindi** — auto-detects language, replies in the farmer's language
- **AI Crop Advisory** — Ollama local LLM with ICAR-grounded knowledge base
- **Knowledge Base** — 15+ crop advisories, pest/disease data, crop calendar
- **Farmer Profiles** — auto-registered on first message, tracks history
- **Admin Dashboard** — Streamlit UI for monitoring, analytics, and broadcast
- **Offline Fallback** — rule-based KB responses when Ollama is down

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python 3.11+) |
| Database | Neon Postgres (serverless) |
| AI Inference | Ollama (llama3.1:8b) |
| WhatsApp | WhatsApp Cloud API (Meta) |
| Admin UI | Streamlit |
| Deployment | Docker Compose |

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Settings (env vars)
│   ├── database.py           # Async SQLAlchemy + Neon Postgres
│   ├── models/               # SQLAlchemy models
│   │   ├── farmer.py
│   │   ├── conversation.py
│   │   ├── crop_advisory.py
│   │   ├── crop_calendar.py
│   │   ├── weather_alert.py
│   │   ├── market_price.py
│   │   └── query_log.py
│   ├── routes/               # API endpoints
│   │   ├── webhook.py        # WhatsApp webhook (receive/send)
│   │   ├── advisory.py       # Advisory query endpoint
│   │   └── admin.py          # Admin/analytics endpoints
│   └── services/             # Business logic
│       ├── language.py       # Telugu/Hindi/English detection
│       ├── intent.py         # Intent classification
│       ├── ollama_client.py  # Ollama LLM integration
│       ├── whatsapp.py       # WhatsApp Cloud API client
│       ├── knowledge_base.py # KB search
│       └── farmer_service.py # Farmer CRUD + query logging
├── admin_dashboard.py        # Streamlit admin UI
├── seed_data.py              # Seed DB with crop advisories
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── PRD.md
```

## Quick Start

### 1. Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- Neon Postgres database ([neon.tech](https://neon.tech))
- WhatsApp Business account with Cloud API access

### 2. Setup

```bash
# Clone the repo
git clone https://github.com/niki241/agri-bot-.git
cd agri-bot-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and fill environment variables
cp .env.example .env
# Edit .env with your Neon DB URL, WhatsApp tokens, etc.
```

### 3. Pull Ollama Model

```bash
ollama pull llama3.1:8b
```

### 4. Seed Database

```bash
python seed_data.py
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Run Admin Dashboard

```bash
streamlit run admin_dashboard.py
```

### 7. Test the Advisory (without WhatsApp)

```bash
curl -X POST http://localhost:8000/api/advisory/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "నా వరి పంటలో ఆకులు పసుపు రంగుకు మారుతున్నాయి",
    "district": "Warangal",
    "state": "Telangana",
    "crops": ["Rice"]
  }'
```

## Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# Pull the Ollama model (first time only)
docker exec kisan-mitra-ollama ollama pull llama3.1:8b

# Seed the database
docker exec kisan-mitra-api python seed_data.py
```

Services:
- **API**: http://localhost:8000
- **Admin**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## WhatsApp Webhook Setup

1. Go to [Meta Developers](https://developers.facebook.com) → your app → WhatsApp → Configuration
2. Set webhook URL: `https://your-domain.com/webhook/whatsapp`
3. Set verify token: same as `WHATSAPP_VERIFY_TOKEN` in `.env`
4. Subscribe to `messages` webhook field

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/webhook/whatsapp` | WhatsApp webhook verification |
| POST | `/webhook/whatsapp` | Receive WhatsApp messages |
| POST | `/api/advisory/query` | Test advisory (no WhatsApp) |
| GET | `/api/farmers` | List all farmers |
| GET | `/api/farmers/{phone}` | Get farmer profile |
| GET | `/api/farmers/{phone}/queries` | Farmer query history |
| GET | `/api/analytics/dashboard` | Dashboard stats |
| POST | `/api/broadcast` | Broadcast message |

## Environment Variables

See `.env.example` for all required variables.

## License

MIT
