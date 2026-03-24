# PRD – Agri Advisory Bot (Kisan Mitra)
**WhatsApp-first AI crop advisory for Indian farmers in Telugu & Hindi**

---

## 1. MVP Overview
**MVP Name**: Kisan Mitra (కిసాన్ మిత్ర / किसान मित्र)  
**One-line pitch**: Farmers send a WhatsApp message (text or voice) about their crop problem → get instant, accurate advisory in Telugu/Hindi within 10 seconds, powered by local AI  
**Target users**: Small & marginal farmers in Telangana, Andhra Pradesh, and Hindi-belt states  
**Distribution**: WhatsApp (primary), direct farmer outreach via FPOs and Krishi Vigyan Kendras  
**Monetization (Phase 2)**: FPO/NGO subscription ₹2,000/mo per 500 farmers; agri-input company lead gen  
**Go-live date**: 14 days from start  

---

## 2. Problem & Opportunity

### The Problem
- **60%** of Indian farmers have no access to timely crop advisory — extension officers cover 1 per 1,000+ farmers  
- Pest/disease misidentification leads to **₹90,000 Cr** annual crop loss (ICAR estimate)  
- Existing solutions (apps, portals) require literacy, smartphones with apps, and English proficiency  
- Farmers already use WhatsApp daily — **400M+ WhatsApp users** in India, penetration even in rural areas  

### The Opportunity
- WhatsApp is zero-friction — no app install, no signup, works on ₹5,000 phones  
- Local LLM inference (Ollama) = **zero per-query cost** after initial setup  
- Telugu/Hindi language support = massive underserved market  
- Government schemes (eNAM, PM-KISAN) actively push digital agriculture  

---

## 3. Core Features

### 3.1 WhatsApp Conversational Interface
- Farmer sends message to bot's WhatsApp Business number  
- Supports: **text messages** (Telugu, Hindi, English), **voice notes** (transcribed via Whisper), **images** (crop photos for disease ID — Phase 2)  
- Bot replies in the **same language** the farmer used  
- Quick-reply buttons for common flows: "పంట సమస్య / फसल समस्या" (Crop Problem), "వాతావరణం / मौसम" (Weather), "మార్కెట్ ధర / बाजार भाव" (Market Price)  

### 3.2 AI Crop Advisory (Ollama Local Inference)
- Farmer describes symptom → LLM identifies likely pest/disease/deficiency  
- Returns: **diagnosis**, **recommended action** (organic + chemical options), **dosage in local units** (గంపలు, बीघा), **urgency level**  
- Context-aware: considers crop type, season (Kharif/Rabi/Zaid), region, soil type  
- Prompt templates grounded with **ICAR/SAU crop protection guides** stored in Postgres  

### 3.3 Knowledge Base (Traditional Layer — Rules + DB)
- Curated crop calendar for major crops: Rice (వరి), Cotton (పత్తి), Chilli (మిర్చి), Wheat (गेहूं), Soybean (सोयाबीन)  
- Pest/disease reference data: 200+ entries with symptoms, images, treatments  
- Government scheme info: PM-KISAN, crop insurance, subsidy deadlines  
- Mandi prices: fetched from eNAM/Agmarknet APIs (daily cache)  

### 3.4 Weather Alerts
- Location-based weather forecast (IMD / OpenWeatherMap)  
- Proactive alerts: "రేపు వర్షం — పురుగుల మందు వేయకండి" (Rain tomorrow — don't spray pesticide)  
- Tied to crop calendar for timing advisories  

### 3.5 Farmer Profile & History
- Auto-created on first message (phone number = unique ID)  
- Tracks: location (mandal/block), crops grown, language preference, past queries  
- Enables personalized follow-ups: "మీ మిర్చి పంటకు 45 రోజులు అయింది — తెగులు తనిఖీ చేయండి"  

### 3.6 Admin Dashboard (Streamlit)
- View all farmer conversations, query volume, top issues  
- Manually review & correct AI responses (human-in-the-loop)  
- Push broadcast messages to farmer segments (e.g., all cotton farmers in Warangal)  
- Analytics: queries/day, language split, crop split, response accuracy  

---

## 4. Technical Architecture

### 4.1 Stack
| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI (Python 3.11+) |
| **Database** | Neon Postgres (serverless) |
| **AI Inference** | Ollama (llama3.1:8b or mistral:7b) running locally |
| **Speech-to-Text** | Whisper (small model, local) |
| **WhatsApp** | WhatsApp Cloud API (Meta Business) |
| **Weather** | OpenWeatherMap API (free tier) |
| **Market Prices** | eNAM API / Agmarknet scraper |
| **Admin UI** | Streamlit |
| **Deployment** | Docker Compose (VPS) |
| **Async Tasks** | FastAPI BackgroundTasks (→ Celery if scale demands) |

### 4.2 Database Schema (Neon Postgres)
```
farmers          — id, phone, name, language, district, state, crops[], created_at
conversations    — id, farmer_id, messages_json, started_at, updated_at
crop_advisories  — id, crop, pest_disease, symptoms_te, symptoms_hi, treatment, dosage, urgency, source
crop_calendar    — id, crop, region, activity, month_start, month_end, description_te, description_hi
weather_alerts   — id, district, alert_type, message_te, message_hi, valid_from, valid_to
market_prices    — id, commodity, market, price, date, source
query_logs       — id, farmer_id, query_text, language_detected, ai_response, response_time_ms, feedback, created_at
```

### 4.3 API Endpoints
```
POST /webhook/whatsapp          — receive incoming WhatsApp messages (Meta webhook)
GET  /webhook/whatsapp           — webhook verification (Meta challenge)
POST /api/advisory/query         — internal: process farmer query → AI response
GET  /api/weather/{district}     — get weather for district
GET  /api/prices/{commodity}     — get mandi prices
GET  /api/farmers                — list farmers (admin)
GET  /api/farmers/{phone}        — farmer profile + history
GET  /api/analytics/dashboard    — aggregated stats for admin
POST /api/broadcast              — send message to farmer segment
GET  /health                     — health check
```

### 4.4 Message Flow
```
Farmer (WhatsApp) 
  → Meta Cloud API webhook 
  → FastAPI /webhook/whatsapp
  → Detect language (fasttext/langdetect)
  → If voice note: download → Whisper transcription
  → Classify intent (crop_problem | weather | price | scheme | greeting)
  → Route to handler:
      crop_problem → Build prompt with farmer context + KB data → Ollama inference → Telugu/Hindi response
      weather      → Fetch from cache/API → format in farmer's language
      price        → Fetch from DB → format
      scheme       → Lookup from KB → format
  → Send reply via WhatsApp Cloud API
  → Log to query_logs
```

---

## 5. Non-Functional Requirements
- **Response time**: < 10 seconds end-to-end (Ollama on 16GB RAM Mac/VPS)  
- **Offline fallback**: If Ollama is down, serve cached KB responses (rule-based matching)  
- **Language**: Telugu and Hindi as primary; English as fallback  
- **Privacy**: No data shared with third parties; farmer can delete data via "డేటా తొలగించు" command  
- **Scale**: Support 1,000 concurrent farmers on single VPS (async FastAPI)  
- **Uptime**: 99% (critical for farmers during crop season)  

---

## 6. Success Metrics (First 30 days)
| Metric | Target |
|--------|--------|
| Farmers onboarded | ≥ 500 |
| Queries answered | ≥ 5,000 |
| Avg response time | < 8 sec |
| Farmer return rate (7-day) | ≥ 40% |
| Advisory accuracy (human-reviewed sample) | ≥ 80% |
| Languages used | Telugu ≥ 50%, Hindi ≥ 30% |

---

## 7. Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Ollama slow on VPS | Use quantized models (Q4_K_M); pre-cache common queries |
| Wrong advisory harms crops | Human-in-the-loop review for first 2 weeks; confidence scoring; disclaimer in every message |
| WhatsApp Cloud API rate limits | Queue + retry with exponential backoff; batch broadcasts |
| Voice note transcription errors | Confirm understanding with farmer before giving advice |
| Farmer trust / adoption | Partner with local FPOs; use familiar Telugu/Hindi tone; add govt scheme info as trust hook |
| eNAM/Agmarknet API downtime | Daily cache of prices; show "last updated" timestamp |

---

## 8. Phased Roadmap

### Phase 1 — MVP (Week 1–2) ← **WE ARE HERE**
- [x] PRD finalized
- [ ] FastAPI backend with WhatsApp webhook
- [ ] Neon Postgres schema + seed data (50 crop advisories)
- [ ] Ollama integration with Telugu/Hindi prompt templates
- [ ] Basic farmer profile (auto-create on first message)
- [ ] Text message flow working end-to-end
- [ ] Streamlit admin: view conversations + query logs
- [ ] Deploy with Docker Compose

### Phase 2 — Enhance (Week 3–4)
- [ ] Voice note support (Whisper)
- [ ] Weather alerts (proactive push)
- [ ] Mandi price lookup
- [ ] Crop calendar reminders
- [ ] Broadcast messaging

### Phase 3 — Scale (Month 2+)
- [ ] Image-based disease detection (vision model)
- [ ] Multi-state expansion
- [ ] FPO subscription billing (Razorpay)
- [ ] Integration with government portals
- [ ] Kannada / Marathi language support

---

## 9. Launch Checklist (Phase 1)
- [ ] FastAPI backend deployed and healthy
- [ ] WhatsApp Business number verified + webhook connected
- [ ] Neon Postgres provisioned with seed data
- [ ] Ollama running with selected model
- [ ] End-to-end test: send WhatsApp message → receive advisory
- [ ] Streamlit admin accessible
- [ ] Telugu + Hindi responses verified by native speaker
- [ ] Error handling: graceful fallback on all failure modes
- [ ] Privacy disclaimer sent on first farmer interaction

---

**Approval to start coding**: Review this PRD and confirm. I will then generate the complete folder structure and build all Phase 1 features.