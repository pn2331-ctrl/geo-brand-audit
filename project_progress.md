# GEO Brand Audit Tool — Project Progress

## What This Is

A Streamlit web app that audits how AI models describe and recommend a brand.
Built on the GEO research framework from NYU Stern Digital Strategy (Spring 2026).

**Core question:** *"Who told AI that?" — and is what it says accurate?*

---

## Current Stack (v2 — as of 2026-04-16)

| Component | Status |
|---|---|
| Claude Sonnet (Anthropic API) | ✅ Working |
| Grok 3 Mini (xAI API) | ✅ Working |
| Streamlit Web App | ✅ Live (local) |
| PDF Export | ✅ Working — purple theme |
| API Key Persistence | ✅ via `~/.streamlit/secrets.toml` |

---

## Scoring Logic (v2)

Three dimensions, all judged by Claude-as-Judge (not keyword matching):

| Dimension | Method | Score |
|---|---|---|
| **Citation Rank** | Judge finds brand position in recommendation list | 1st=10, 2nd=8, 3rd=6, 4th=4, 5th=2, absent=0 |
| **Accuracy** | Judge rates specificity and correctness of AI description | 0–10 |
| **Head-to-Head** | Judge determines who wins direct comparison (optional) | 10/5/0 |

**GEO Score formula:**
- With competitor: `(Citation × 0.4) + (Accuracy × 0.4) + (H2H × 0.2)` × 10
- Without competitor: `(Citation + Accuracy) / 2` × 10

**Four-Quadrant Diagnosis** derived from Citation Rank and Accuracy thresholds (≥5 = HIGH).

---

## Files

| File | Description |
|---|---|
| `app.py` | Main Streamlit app |
| `GEO.ipynb` | Original exploration notebook |
| `GEO_mindmap.mm` | FreeMind mind map from PPT research |
| `images/geo_quadrant.png` | Purple-themed quadrant chart (matplotlib) |
| `README.md` | English README with embedded quadrant image |
| `requirements.txt` | `streamlit`, `anthropic`, `openai`, `fpdf2` |
| `.streamlit/secrets.toml` | API keys (gitignored) |

---

## Session Log

### 2026-04-16
- Switched second model from Gemini → Grok (xAI, cheaper)
- Built Streamlit web app (`app.py`) with sidebar key input
- Added API key persistence via `secrets.toml`
- **P1 fixes:**
  - Fixed markdown rendering in raw responses (stripped `##`, `**` etc.)
  - Labeled awareness query as "context only — not scored"
- **P2 — GEO Score 0–100:**
  - Replaced YES/NO scoring with Claude-as-Judge numeric scoring (0–10 per dimension)
  - Citation Rank: judge finds brand's position in recommendation list
  - Accuracy: judge rates description quality 0–10
  - Head-to-Head: judge scores winner 0/5/10
  - Without competitor: Citation Rank replaces Head-to-Head as implicit competitive signal
- **PDF export:**
  - Full report: scores, diagnosis, raw AI responses
  - Purple color theme (`#3E266E` base), gray for missing/low
  - Fixed markdown stripping in PDF output (was printing `**` asterisks literally)
- **Research assets:**
  - Generated `GEO_mindmap.mm` from PPT (`the-invisible-shelf-copy copy.pptx`)
  - Generated `images/geo_quadrant.png` — purple-themed quadrant chart
  - Rewrote `README.md` in English with embedded chart, scoring methodology section

### Earlier sessions
- v1 notebook: Claude + Grok dual model, basic YES/NO scoring
- Model upgraded haiku → sonnet-4-6 (haiku didn't recognize Rhode)
- Accuracy judge added after string-match false positives on Dr. Althea and Rhode

---

## Remaining Work

### P3 — Complete Project
- [ ] Deploy to Streamlit Community Cloud (free public URL for portfolio)
- [ ] Add app screenshots to README
- [ ] Push to GitHub (secrets.toml is gitignored — safe to push)

### P4 — Nice to Have
- [ ] Add ChatGPT / Gemini as additional models
- [ ] Audit history — save results with timestamp for trend tracking
- [ ] Multi-brand batch audit
