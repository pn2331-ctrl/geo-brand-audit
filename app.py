import re
import datetime
import streamlit as st
import anthropic
from openai import OpenAI
from fpdf import FPDF

st.set_page_config(
    page_title="GEO Brand Audit",
    page_icon="🔍",
    layout="wide"
)

CUSTOM_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

*, *::before, *::after {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Full-page gradient */
.stApp {
    background: linear-gradient(135deg, #CEC0DE 0%, #F5F0FA 48%, #F0C2CE 100%) fixed;
    min-height: 100vh;
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.72) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(210,195,230,0.45) !important;
}

#MainMenu, footer { visibility: hidden; }

/* Hero */
.geo-hero {
    text-align: center;
    padding: 3.2rem 2rem 2.4rem;
    margin-bottom: 1.2rem;
}
.geo-hero h1 {
    font-size: 2.7rem;
    font-weight: 900;
    color: #1C1828;
    margin: 0 0 0.9rem;
    line-height: 1.15;
    letter-spacing: -0.8px;
}
.geo-hero p {
    font-size: 1.05rem;
    color: #8A7898;
    line-height: 1.7;
    margin: 0 auto;
    max-width: 500px;
}

/* Cards */
.score-card {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-radius: 18px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    box-shadow: 0 4px 32px rgba(180,150,210,0.10), 0 1px 4px rgba(0,0,0,0.03);
    border: 1px solid rgba(215,200,235,0.6);
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.75) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(215,200,235,0.55) !important;
    backdrop-filter: blur(14px) !important;
    box-shadow: 0 2px 20px rgba(180,150,210,0.08) !important;
}

.model-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #A090B8;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

.geo-score-ring {
    width: 112px; height: 112px; border-radius: 50%;
    background: linear-gradient(145deg, #C4B2D8, #E8B4C8);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    margin: 0 auto 1.4rem;
    box-shadow: 0 8px 28px rgba(196,178,216,0.40);
}
.geo-score-number { font-size: 2.35rem; font-weight: 900; color: white; line-height: 1; }
.geo-score-label  { font-size: 0.52rem; color: rgba(255,255,255,0.78); letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }

.sub-scores { margin: 0 0 1.2rem; }
.sub-score-row { display: flex; align-items: center; margin: 0.45rem 0; gap: 0.55rem; text-align: left; }
.sub-score-name { font-size: 0.73rem; color: #A898B8; width: 90px; flex-shrink: 0; text-align: right; }
.sub-score-bar-bg { flex: 1; background: rgba(210,195,230,0.3); border-radius: 99px; height: 6px; overflow: hidden; }
.sub-score-bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #E4B8CC, #C4B2D8); }
.sub-score-val { font-size: 0.73rem; font-weight: 700; color: #8A78A8; width: 30px; flex-shrink: 0; }

.diag-badge {
    display: inline-block; padding: 0.28rem 0.9rem;
    border-radius: 99px; font-size: 0.77rem; font-weight: 600;
    margin: 0.3rem 0 0.5rem;
}
.diag-geo-ready     { background: rgba(196,178,216,0.22); color: #7B5FA8; border: 1px solid rgba(196,178,216,0.5); }
.diag-accurate      { background: rgba(200,185,220,0.2);  color: #9080B0; border: 1px solid rgba(200,185,220,0.45); }
.diag-visible-wrong { background: rgba(240,185,195,0.22); color: #A85870; border: 1px solid rgba(240,185,195,0.5); }
.diag-invisible     { background: rgba(180,175,190,0.2);  color: #8A8098; border: 1px solid rgba(180,175,190,0.45); }

.advice-text { font-size: 0.79rem; color: #9A90A8; line-height: 1.6; margin: 0; }

.section-header {
    font-size: 0.7rem; font-weight: 700;
    color: #A090B8; letter-spacing: 1.8px;
    text-transform: uppercase;
    margin: 2rem 0 0.8rem;
}

.divider-line { border: none; border-top: 1px solid rgba(210,195,230,0.4); margin: 1.6rem 0; }

[data-testid="stDownloadButton"] button,
[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #C4B2D8, #E8B0C4) !important;
    color: white !important; border: none !important;
    border-radius: 99px !important; font-weight: 700 !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 16px rgba(196,178,216,0.35) !important;
}

/* Sidebar text */
[data-testid="stSidebar"] h3 { color: #1C1828 !important; font-weight: 700 !important; }
</style>"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────
st.markdown("""
<div class="geo-hero">
    <h1>Who told AI that about your brand<br>— and is it actually true?</h1>
    <p>See how Claude and Grok discover, describe, and recommend your brand — scored with the GEO diagnostic framework.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
try:
    _ant_secret = st.secrets.get("ANTHROPIC_API_KEY", "")
    _xai_secret = st.secrets.get("XAI_API_KEY", "")
except Exception:
    _ant_secret = ""
    _xai_secret = ""

with st.sidebar:
    st.markdown("### API Keys")
    if _ant_secret and _xai_secret:
        st.success("Keys loaded from secrets.")
        anthropic_key = _ant_secret
        xai_key       = _xai_secret
    else:
        anthropic_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        xai_key       = st.text_input("xAI API Key",       type="password", placeholder="xai-...")
        st.caption("Keys are used only for this session and never stored.")
    st.divider()
    st.caption("Built on GEO research · NYU Stern Digital Strategy, Spring 2026.")

# ── Inputs ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Brand Info</div>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        brand    = st.text_input("Brand Name",     placeholder="e.g. CeraVe")
        category = st.text_input("Market Context", placeholder="e.g. sensitive skin, electric vehicles")
    with col2:
        product    = st.text_input("Product Type",         placeholder="e.g. moisturizer")
        competitor = st.text_input("Competitor (optional)", placeholder="e.g. La Roche-Posay")

keys_ready   = bool(anthropic_key and xai_key)
inputs_ready = bool(brand and category and product)
run_button   = st.button("Run Audit", type="primary", disabled=not (keys_ready and inputs_ready), use_container_width=True)

if not keys_ready:
    st.info("Enter your API keys in the sidebar to get started.")


# ── Backend ───────────────────────────────────────────────────────

def ask_claude(client, prompt):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def ask_grok(client, prompt):
    response = client.chat.completions.create(
        model="grok-3-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def build_queries(brand, category, product, competitor=None):
    queries = [
        {"type": "awareness",       "prompt": f"What is {brand}? Describe what they do in {category} in 2-3 sentences."},
        {"type": "recommendation",  "prompt": f"What are the best {product} brands for {category}? List 5 specific brand names and why you recommend each."},
        {"type": "evaluation",      "prompt": f"Is {brand} a good {product} for {category}? What are their strengths and weaknesses?"},
    ]
    if competitor:
        queries.append({"type": "comparison", "prompt": f"{brand} vs {competitor} as a {product} for {category}: which would you recommend and why?"})
    return queries


def run_audit(ant_client, grok_client, brand, category, product, competitor=None):
    queries = build_queries(brand, category, product, competitor)
    results = []
    for q in queries:
        results.append({
            "type":   q["type"],
            "prompt": q["prompt"],
            "claude": ask_claude(ant_client, q["prompt"]),
            "grok":   ask_grok(grok_client, q["prompt"])
        })
    return results


def score_accuracy(ant_client, brand, evaluation_text):
    judge_prompt = (
        f"Rate how accurately and specifically this AI response describes the brand '{brand}'.\n\n"
        "Scoring guide:\n"
        f"9-10: Mentions specific products, ingredients, founders, positioning, or use cases of {brand} accurately\n"
        f"6-8: Mentions some brand-specific details but incomplete or partially vague\n"
        f"3-5: Mostly generic advice with minimal brand-specific content\n"
        f"0-2: No brand-specific info, says it doesn't know {brand}, or provides wrong information\n\n"
        "Important: ignore opening disclaimers — focus on whether brand-specific facts appear anywhere.\n\n"
        "Answer with ONLY a single integer from 0 to 10.\n\n"
        f"Response: {evaluation_text}"
    )
    try:
        result = ask_claude(ant_client, judge_prompt).strip()
        return max(0, min(10, int(re.search(r'\d+', result).group())))
    except Exception:
        return 0


def score_citation_rank(ant_client, brand, recommendation_text):
    judge_prompt = (
        f"In this AI recommendation response, find '{brand}' in the list of recommended brands.\n"
        "What position is it mentioned?\n\n"
        "Answer with ONLY a single integer:\n"
        "1 = first mentioned, 2 = second, 3 = third, 4 = fourth, 5 = fifth, 0 = not mentioned\n\n"
        f"Response: {recommendation_text}"
    )
    try:
        result = ask_claude(ant_client, judge_prompt).strip()
        pos = max(0, min(5, int(re.search(r'\d+', result).group())))
        return {0: 0, 1: 10, 2: 8, 3: 6, 4: 4, 5: 2}[pos]
    except Exception:
        return 0


def score_head_to_head(ant_client, brand, comparison_text):
    judge_prompt = (
        f"In this comparison response, how strongly is '{brand}' recommended over the competitor?\n\n"
        "Answer with ONLY a single integer:\n"
        f"10 = {brand} is clearly recommended\n"
        "5 = it's a tie or depends on use case\n"
        "0 = the competitor is clearly recommended\n\n"
        f"Response: {comparison_text}"
    )
    try:
        result = ask_claude(ant_client, judge_prompt).strip()
        return max(0, min(10, int(re.search(r'\d+', result).group())))
    except Exception:
        return 5


def score_model(ant_client, brand, results, model_key):
    scores = {}
    for r in results:
        resp = r[model_key]
        if r["type"] == "recommendation":
            scores["citation"] = score_citation_rank(ant_client, brand, resp)
        elif r["type"] == "evaluation":
            scores["accuracy"] = score_accuracy(ant_client, brand, resp)
        elif r["type"] == "comparison":
            scores["head_to_head"] = score_head_to_head(ant_client, brand, resp)

    citation = scores.get("citation", 0)
    accuracy = scores.get("accuracy", 0)

    if "head_to_head" in scores:
        h2h = scores["head_to_head"]
        geo_score = round(citation * 0.4 + accuracy * 0.4 + h2h * 0.2) * 10
    else:
        geo_score = round((citation + accuracy) / 2) * 10

    visibility     = "HIGH" if citation >= 5 else "LOW"
    accuracy_level = "HIGH" if accuracy >= 5 else "LOW"

    quadrant_map = {
        ("HIGH", "HIGH"): "GEO Ready",
        ("HIGH", "LOW"):  "Visible but Wrong",
        ("LOW",  "HIGH"): "Accurate but Missing",
        ("LOW",  "LOW"):  "Invisible & Misrepresented",
    }

    return {
        "geo_score":    geo_score,
        "citation":     citation,
        "accuracy":     accuracy,
        "head_to_head": scores.get("head_to_head"),
        "diagnosis":    quadrant_map[(visibility, accuracy_level)],
    }


DIAGNOSIS_INFO = {
    "GEO Ready": {
        "emoji": "✅", "css": "diag-geo-ready",
        "advice": "AI models know your brand, recommend it unprompted, and describe it accurately. Monitor regularly to maintain this position."
    },
    "Visible but Wrong": {
        "emoji": "⚠️", "css": "diag-visible-wrong",
        "advice": "AI recommends your brand but describes it inaccurately. Most dangerous outcome — audit and correct the information sources AI is learning from."
    },
    "Accurate but Missing": {
        "emoji": "📉", "css": "diag-accurate",
        "advice": "AI describes your brand accurately but doesn't recommend it unprompted. Increase third-party content coverage to boost visibility."
    },
    "Invisible & Misrepresented": {
        "emoji": "❌", "css": "diag-invisible",
        "advice": "AI doesn't know or recommend your brand. Build foundational content presence from scratch."
    },
}


def render_score_card(model_name, scores):
    geo      = scores["geo_score"]
    citation = scores["citation"]
    accuracy = scores["accuracy"]
    h2h      = scores["head_to_head"]
    diag     = scores["diagnosis"]
    info     = DIAGNOSIS_INFO[diag]

    h2h_html = ""
    if h2h is not None:
        h2h_html = f"""
        <div class="sub-score-row">
            <span class="sub-score-name">Head-to-Head</span>
            <div class="sub-score-bar-bg">
                <div class="sub-score-bar-fill" style="width:{h2h * 10}%"></div>
            </div>
            <span class="sub-score-val">{h2h}/10</span>
        </div>"""

    return f"""
    <div class="score-card">
        <div class="model-label">{model_name}</div>
        <div class="geo-score-ring">
            <span class="geo-score-number">{geo}</span>
            <span class="geo-score-label">GEO Score</span>
        </div>
        <div class="sub-scores">
            <div class="sub-score-row">
                <span class="sub-score-name">Citation Rank</span>
                <div class="sub-score-bar-bg">
                    <div class="sub-score-bar-fill" style="width:{citation * 10}%"></div>
                </div>
                <span class="sub-score-val">{citation}/10</span>
            </div>
            <div class="sub-score-row">
                <span class="sub-score-name">Accuracy</span>
                <div class="sub-score-bar-bg">
                    <div class="sub-score-bar-fill" style="width:{accuracy * 10}%"></div>
                </div>
                <span class="sub-score-val">{accuracy}/10</span>
            </div>
            {h2h_html}
        </div>
        <span class="diag-badge {info['css']}">{info['emoji']} {diag}</span>
        <p class="advice-text">{info['advice']}</p>
    </div>"""


# ── PDF Export ────────────────────────────────────────────────────

def _safe(text):
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_markdown(text):
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*(.*?)\*\*',     r'\1', text)
    text = re.sub(r'\*(.*?)\*',         r'\1', text)
    text = re.sub(r'_(.*?)_',           r'\1', text)
    text = re.sub(r'`([^`]*)`',         r'\1', text)
    text = re.sub(r'(?m)^#{1,6}\s+',   '',    text)
    text = re.sub(r'(?m)^\s*[-*+]\s+', '- ',  text)
    return text.strip()


P_DARK  = (62,  38, 110)
P_MID   = (105, 70, 165)
P_SOFT  = (158, 125, 210)
P_LIGHT = (224, 215, 245)
P_PALE  = (246, 243, 252)
G_DARK  = (65,  65,  70)
G_MID   = (145, 145, 150)
G_LIGHT = (220, 220, 224)


def _section_title(pdf, title):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(*P_DARK)
    pdf.cell(0, 7, f"  {title}", fill=True, ln=True)
    pdf.set_text_color(*G_DARK)
    pdf.ln(3)


def _score_color(score, max_val=10):
    ratio = score / max_val
    if ratio >= 0.7:   return P_DARK
    elif ratio >= 0.4: return P_SOFT
    else:              return G_MID


DIAG_COLOR = {
    "GEO Ready":                  P_DARK,
    "Accurate but Missing":       P_MID,
    "Visible but Wrong":          P_SOFT,
    "Invisible & Misrepresented": G_MID,
}


def generate_pdf(brand, category, product, competitor, results, claude_scores, grok_scores):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    LEFT = 15
    W    = pdf.w - 30

    pdf.set_fill_color(*P_DARK)
    pdf.rect(0, 0, pdf.w, 28, "F")
    pdf.set_xy(0, 6)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 9, "AI Brand Footprint Audit", align="C", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*P_LIGHT)
    pdf.cell(0, 6, f"GEO Diagnostic Report   |   {datetime.date.today()}", align="C", ln=True)
    pdf.ln(8)

    pdf.set_text_color(*P_DARK)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _safe(brand), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*G_MID)
    meta = f"{product}   |   {category}"
    if competitor:
        meta += f"   |   vs. {competitor}"
    pdf.cell(0, 6, _safe(meta), ln=True)
    pdf.set_draw_color(*P_LIGHT)
    pdf.ln(3)
    pdf.line(LEFT, pdf.get_y(), LEFT + W, pdf.get_y())
    pdf.ln(5)

    _section_title(pdf, "GEO SCORES")
    cw = [W * 0.38, W * 0.31, W * 0.31]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*P_LIGHT)
    pdf.set_text_color(*P_DARK)
    pdf.cell(cw[0], 7, "",       border="B", fill=True)
    pdf.cell(cw[1], 7, "Claude", border="B", fill=True, align="C")
    pdf.cell(cw[2], 7, "Grok",   border="B", fill=True, align="C", ln=True)

    score_rows = [
        ("GEO Score",     claude_scores["geo_score"], grok_scores["geo_score"], 100),
        ("Citation Rank", claude_scores["citation"],  grok_scores["citation"],  10),
        ("Accuracy",      claude_scores["accuracy"],  grok_scores["accuracy"],  10),
    ]
    if claude_scores["head_to_head"] is not None:
        score_rows.append(("Head-to-Head", claude_scores["head_to_head"], grok_scores["head_to_head"], 10))

    for i, (label, cv, gv, mx) in enumerate(score_rows):
        fill_bg = P_PALE if i % 2 == 0 else (255, 255, 255)
        row_h   = 8 if label == "GEO Score" else 7
        fsize   = 11 if label == "GEO Score" else 9
        fbold   = "B" if label == "GEO Score" else ""
        pdf.set_fill_color(*fill_bg)
        pdf.set_text_color(*G_DARK)
        pdf.set_font("Helvetica", fbold, fsize)
        pdf.cell(cw[0], row_h, label, fill=True)
        for val in (cv, gv):
            pdf.set_text_color(*_score_color(val, mx))
            pdf.set_font("Helvetica", "B", fsize)
            pdf.cell(cw[1] if val == cv else cw[2], row_h, f"{val} / {mx}", fill=True, align="C")
        pdf.ln()

    pdf.set_text_color(*G_DARK)
    pdf.ln(6)

    _section_title(pdf, "DIAGNOSIS")
    for model_name, scores in [("Claude", claude_scores), ("Grok", grok_scores)]:
        diag        = scores["diagnosis"]
        dr, dg, db  = DIAG_COLOR.get(diag, (80, 80, 80))
        advice      = DIAGNOSIS_INFO[diag]["advice"]
        pdf.set_fill_color(dr, dg, db)
        bar_y = pdf.get_y()
        pdf.rect(LEFT, bar_y, 3, 22, "F")
        pdf.set_x(LEFT + 6)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*G_DARK)
        pdf.cell(W - 6, 6, model_name, ln=True)
        pdf.set_x(LEFT + 6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(dr, dg, db)
        pdf.cell(W - 6, 5, diag, ln=True)
        pdf.set_x(LEFT + 6)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*G_MID)
        pdf.multi_cell(W - 6, 4, _safe(advice))
        pdf.ln(4)

    pdf.set_text_color(*G_DARK)
    pdf.ln(2)

    _section_title(pdf, "RAW AI RESPONSES")
    for r in results:
        type_label = r["type"].upper()
        if r["type"] == "awareness":
            type_label += "  (context only — not scored)"
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*P_DARK)
        pdf.set_fill_color(*P_LIGHT)
        pdf.cell(0, 6, f"  {type_label}", fill=True, ln=True)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*G_MID)
        pdf.set_x(LEFT + 3)
        pdf.multi_cell(W - 3, 4, _safe(r["prompt"]))
        pdf.ln(2)
        for model_name, key in [("Claude", "claude"), ("Grok", "grok")]:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*P_MID)
            pdf.cell(0, 5, model_name, ln=True)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(*G_DARK)
            pdf.multi_cell(0, 5, _safe(_strip_markdown(r[key])))
            pdf.ln(2)
        pdf.set_draw_color(*G_LIGHT)
        pdf.line(LEFT, pdf.get_y(), LEFT + W, pdf.get_y())
        pdf.ln(4)

    return bytes(pdf.output())


# ── Run & Display ─────────────────────────────────────────────────

if run_button:
    ant_client  = anthropic.Anthropic(api_key=anthropic_key)
    grok_client = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")

    with st.spinner("Querying Claude and Grok..."):
        results = run_audit(ant_client, grok_client, brand, category, product, competitor or None)

    with st.spinner("Scoring results..."):
        claude_scores = score_model(ant_client, brand, results, "claude")
        grok_scores   = score_model(ant_client, brand, results, "grok")

    st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)

    col_claude, col_grok = st.columns(2)
    with col_claude:
        st.markdown(render_score_card("Claude", claude_scores), unsafe_allow_html=True)
    with col_grok:
        st.markdown(render_score_card("Grok", grok_scores), unsafe_allow_html=True)

    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Raw AI Responses</div>', unsafe_allow_html=True)

    for r in results:
        label = f"[{r['type'].upper()}]  {r['prompt'][:70]}..."
        if r["type"] == "awareness":
            label += "  *(context only — not scored)*"
        with st.expander(label):
            def clean(text):
                return re.sub(r"(?m)^#{1,6}\s+", "", text)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Claude**")
                st.markdown(clean(r["claude"]))
            with c2:
                st.markdown("**Grok**")
                st.markdown(clean(r["grok"]))

    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    pdf_bytes = generate_pdf(
        brand, category, product, competitor or None,
        results, claude_scores, grok_scores
    )
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"geo_audit_{brand.lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
