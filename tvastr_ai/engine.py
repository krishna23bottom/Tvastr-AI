"""TVASTR AI core: intent classification + context detection + prompt building + LLM call."""
import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import prompts
from knowledge_base import KNOWLEDGE, CONTEXT_TIPS, FILM_VOCAB
from llm_client import LLMError, active_provider, generate

BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "intent_dataset_expanded.csv"  # starter set + 180 added examples
MODEL_PATH = BASE / "models" / "intent_model.joblib"

CONF_THRESHOLD = 0.15     # below this the intent is treated as "unclear"
SECOND_INTENT_MIN = 0.15  # report a 2nd intent if it is at least this likely
MAX_INPUT_CHARS = 1000
MAX_HISTORY_TURNS = 6

# ----------------------------------------------------------------------------
# 1) Supervised intent classifier  (TF-IDF + Logistic Regression)
# ----------------------------------------------------------------------------

def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True,
                                  stop_words="english")),
        ("clf", LogisticRegression(max_iter=2000, C=10.0)),
    ])


def train_and_save():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    model = build_pipeline().fit(df["text"], df["intent"])
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return train_and_save()


# ----------------------------------------------------------------------------
# 2) Context detection (project type, genre, mood, setting, resources)
# ----------------------------------------------------------------------------
CONTEXT_KEYWORDS = {
    "project": {
        "music_video": ["music video", "rap video", "song", "rapper", "lyrics", "track", "mv"],
        "short_film": ["short film"],
        "documentary": ["documentary", "doc"],
        "reel": ["reel", "reels", "shorts", "tiktok", "instagram"],
        "commercial": ["commercial", "advert", "ad", "brand", "product video"],
        "vlog": ["vlog", "youtube"],
        "wedding": ["wedding"],
        "portrait": ["portrait"],
        "film": ["film", "movie"],
    },
    "genre": {
        "hip-hop": ["hip-hop", "hip hop", "hiphop", "rap", "trap", "drill"],
        "rock": ["rock", "metal"],
        "pop": ["pop"],
        "edm": ["edm", "electronic"],
        "lo-fi": ["lo-fi", "lofi"],
    },
    "mood": {
        "dark": ["dark", "moody", "dim"],
        "aggressive": ["aggressive", "intense", "angry", "powerful"],
        "cinematic": ["cinematic"],
        "isolated": ["isolated", "isolation", "lonely", "alone", "loneliness"],
        "nostalgic": ["nostalgic", "nostalgia", "vintage", "retro"],
        "gritty": ["gritty", "raw", "grainy"],
        "romantic": ["romantic", "love"],
        "tense": ["tense", "suspense", "thriller", "scary", "horror"],
        "happy": ["happy", "joyful", "fun", "colorful", "bright"],
    },
    "setting": {
        "night": ["night", "nighttime", "midnight", "after dark"],
        "day": ["daytime", "sunny", "golden hour", "sunset"],
        "outdoor": ["outdoor", "outdoors", "street", "parking lot", "rooftop", "forest"],
        "indoor": ["indoor", "indoors", "studio", "room", "apartment"],
        "interview": ["interview"],
    },
    "resources": {
        "car": ["car", "cars", "vehicle"],
        "one artist": ["one artist", "single artist", "solo", "one actor", "one person"],
        "phone": ["phone", "iphone", "smartphone"],
        "low budget": ["low budget", "cheap", "no budget", "tight budget", "small crew"],
        "one light": ["one led", "single light", "one light"],
        "gimbal": ["gimbal"],
        "drone": ["drone"],
    },
}


def _has(text, kw):
    return re.search(rf"(?<![\w-]){re.escape(kw)}(?![\w-])", text) is not None


def detect_context(text):
    t = text.lower()
    ctx = {}
    for group, table in CONTEXT_KEYWORDS.items():
        hits = [label for label, kws in table.items() if any(_has(t, k) for k in kws)]
        if group == "project" and len(hits) > 1:
            # prefer the most specific type over generic 'film'
            hits = [h for h in hits if h != "film"] or hits
        if hits:
            ctx[group] = hits
    return ctx


def merge_context(old, new):
    """Keep context across turns so the bot stays context-aware."""
    merged = {k: list(v) for k, v in (old or {}).items()}
    for k, vals in new.items():
        merged[k] = list(dict.fromkeys(vals + merged.get(k, [])))[:4]
    return merged


def context_to_text(ctx):
    return ", ".join(v.replace("_", " ") for vals in ctx.values() for v in vals)


# ----------------------------------------------------------------------------
# 3) Small talk / safety checks
# ----------------------------------------------------------------------------
GREETING_RE = re.compile(r"^\s*(hi|hello|hey|namaste|yo|good (morning|evening|afternoon))\b[\s!.,]*$", re.I)
THANKS_RE = re.compile(r"^\s*(thanks|thank you|thx|ok thanks|great thanks)\b[\s!.]*$", re.I)

GREETING_REPLY = ("Hi! I'm **TVASTR AI**, your co-pilot for visual storytelling. "
                  "Ask me about shots, camera settings, lighting, editing, color grading, sound or music videos.\n\n"
                  "Try: *\"I'm shooting a hip-hop music video at night with one artist and a car.\"*")
THANKS_REPLY = "Happy to help! Send me the next scene or problem whenever you're ready."
OUT_OF_SCOPE_REPLY = ("That looks outside my area. I'm built for **filmmaking and video production** "
                      "(shots, camera, lighting, editing, color, sound, export).\n\n"
                      "Try rephrasing it as a filmmaking question, for example: "
                      "*\"How should I light an interview with one LED?\"*")
UNCLEAR_REPLY = ("I want to help, but I'm not sure what you need yet. Are you asking about "
                 "**shots, camera settings, lighting, editing, color grading, sound, music videos, "
                 "or export**? Add a bit more detail (project type, mood, location) and I'll tailor the answer.")


def has_film_vocab(text):
    words = re.findall(r"[a-z]+", text.lower())
    return any(w in FILM_VOCAB or w.rstrip("s") in FILM_VOCAB for w in words)


# ----------------------------------------------------------------------------
# 4) Engine
# ----------------------------------------------------------------------------
class TvastrEngine:
    def __init__(self):
        self.model = load_model()

    def classify(self, text):
        probs = self.model.predict_proba([text])[0]
        order = probs.argsort()[::-1]
        classes = self.model.classes_
        top = (classes[order[0]], float(probs[order[0]]))
        second = (classes[order[1]], float(probs[order[1]]))
        return top, second

    def _offline_reply(self, intent, ctx):
        k = KNOWLEDGE[intent]
        lines = [f"**{k['title']}**"]
        if ctx:
            lines.append(f"What I picked up: {context_to_text(ctx)}")
        lines += [f"- {t}" for t in k["tips"]]
        extras = [CONTEXT_TIPS[v] for vals in ctx.values() for v in vals if v in CONTEXT_TIPS][:3]
        if extras:
            lines.append("\n**For your situation:**")
            lines += [f"- {e}" for e in extras]
        lines.append(f"\n{k['follow_up']}")
        return "\n".join(lines)

    def respond(self, text, history=None, ctx=None):
        """Return a dict with reply + debug info. Never raises."""
        history = history or []
        base = {"intent": None, "confidence": 0.0, "second_intent": None, "context": ctx or {},
                "source": "rule", "prompt_version": prompts.PROMPT_VERSION}

        # --- input validation
        text = (text or "").strip()
        if not text:
            return {**base, "reply": "Please type a question about your film or video project.", "source": "validation"}
        if len(text) > MAX_INPUT_CHARS:
            return {**base, "reply": f"That message is too long. Please keep it under {MAX_INPUT_CHARS} characters.",
                    "source": "validation"}
        if GREETING_RE.match(text):
            return {**base, "reply": GREETING_REPLY}
        if THANKS_RE.match(text):
            return {**base, "reply": THANKS_REPLY}

        # --- understand the request
        (intent, conf), (intent2, conf2) = self.classify(text)
        new_ctx = detect_context(text)
        ctx = merge_context(ctx, new_ctx)
        base.update(intent=intent, confidence=conf, context=ctx,
                    second_intent=intent2 if conf2 >= SECOND_INTENT_MIN else None)

        unclear = conf < CONF_THRESHOLD
        if conf < 0.5 and not has_film_vocab(text) and not new_ctx:
            return {**base, "intent": None, "reply": OUT_OF_SCOPE_REPLY}

        provider = active_provider()
        if provider != "offline":
            notes = list(KNOWLEDGE[intent]["tips"])
            if base["second_intent"]:
                notes += KNOWLEDGE[base["second_intent"]]["tips"][:2]
            label = KNOWLEDGE[intent]["title"] + (
                f" + {KNOWLEDGE[base['second_intent']]['title']}" if base["second_intent"] else "")
            if unclear:
                label = "unclear (ask a clarifying question)"
            messages = [{"role": m["role"], "content": m["content"]}
                        for m in history[-2 * MAX_HISTORY_TURNS:]]
            messages.append({"role": "user", "content": prompts.user_prompt(
                text, label, conf, context_to_text(ctx), notes)})
            try:
                reply = generate(prompts.system_prompt(), messages, provider=provider)
                return {**base, "reply": reply, "source": f"llm:{provider}"}
            except LLMError as e:
                fallback = UNCLEAR_REPLY if unclear else self._offline_reply(intent, ctx)
                return {**base, "reply": f"{fallback}\n\n_(Note: {e} Showing my built-in guidance instead.)_",
                        "source": "fallback"}
            except Exception:
                pass  # any unexpected error -> fall through to offline answer

        reply = UNCLEAR_REPLY if unclear else self._offline_reply(intent, ctx)
        return {**base, "reply": reply, "source": "offline" if provider == "offline" else "fallback"}
