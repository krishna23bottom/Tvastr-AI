"""API-based LLM integration with error handling.

Supported providers (set LLM_PROVIDER or let it auto-detect from the key you export):
  gemini     -> env GEMINI_API_KEY (or GOOGLE_API_KEY), optional GEMINI_MODEL
  anthropic  -> env ANTHROPIC_API_KEY, optional ANTHROPIC_MODEL
  offline    -> no API; the bot answers from its own knowledge base
"""
import os
import time
import requests


class LLMError(Exception):
    """Raised with a user-friendly message when the LLM call fails."""


def active_provider():
    p = os.getenv("LLM_PROVIDER", "auto").lower()
    if p != "auto":
        return p
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "offline"


def _post(url, headers, payload, timeout, retries):
    last = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.Timeout:
            last = LLMError("The AI service took too long to respond.")
        except requests.ConnectionError:
            last = LLMError("Could not reach the AI service. Check your internet connection.")
        else:
            if r.status_code == 200:
                return r.json()
            if r.status_code in (401, 403):
                raise LLMError("The API key was rejected. Check that your key is correct.")
            if r.status_code == 429:
                last = LLMError("Rate limit reached. Please wait a moment and try again.")
            elif r.status_code >= 500:
                last = LLMError("The AI service is having trouble right now.")
            else:
                raise LLMError(f"The AI service returned an error ({r.status_code}).")
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise last


def _gemini(system, messages, timeout, retries, max_tokens, temperature):
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    contents = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    data = _post(url, {"x-goog-api-key": key, "Content-Type": "application/json"},
                 payload, timeout, retries)
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError, TypeError):
        raise LLMError("The AI returned an empty or blocked response. Try rephrasing.")
    if not text:
        raise LLMError("The AI returned an empty response. Try rephrasing.")
    return text


def _anthropic(system, messages, timeout, retries, max_tokens, temperature):
    key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01",
               "content-type": "application/json"}
    payload = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
               "system": system, "messages": messages}
    data = _post("https://api.anthropic.com/v1/messages", headers, payload, timeout, retries)
    try:
        text = "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text").strip()
    except (KeyError, TypeError):
        raise LLMError("The AI returned an unexpected response.")
    if not text:
        raise LLMError("The AI returned an empty response. Try rephrasing.")
    return text


def generate(system, messages, provider=None, timeout=30, retries=2,
             max_tokens=1024, temperature=0.7):
    """messages = [{'role': 'user'|'assistant', 'content': str}, ...] ending with a user turn."""
    provider = provider or active_provider()
    if provider == "gemini":
        return _gemini(system, messages, timeout, retries, max_tokens, temperature)
    if provider == "anthropic":
        return _anthropic(system, messages, timeout, retries, max_tokens, temperature)
    raise LLMError("No LLM provider configured.")
