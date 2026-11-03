# TVASTR AI - Your AI Co-Pilot for Visual Storytelling
IAI Assignment 3: AI Chatbot using Prompt Engineering (Python, Flask, scikit-learn, LLM API)

## 1. Domain
Filmmaking and video production: concept, shots, angles, movement, composition, camera settings,
lighting, color grading, editing, sound, storyboards/shot lists, music videos, troubleshooting,
export and equipment.

## 2. Conversation flow
User text -> input validation -> TF-IDF + Logistic Regression intent classifier (15 intents)
-> context detector (project type, genre, mood, setting, resources; remembered across turns)
-> prompt builder (system prompt + detected intent + context + knowledge notes + chat history)
-> LLM API (Gemini or Claude) -> reply.
If no API key is set or the API fails, the bot answers from its built-in knowledge base.

## 3. Prompt engineering
| Version | Prompt | Behaviour |
|---|---|---|
| v1 (baseline) | "You are a filmmaking assistant. Answer the user's question." | Generic, long, no follow-up, may drift off-topic |
| v2 (final) | Role + scope + rules + output format + few-shot example + injected [DETECTED INTENT]/[DETECTED CONTEXT]/[REFERENCE NOTES] | Specific to the user's setup, under 200 words, bullets + pro tip + one follow-up question, refuses out-of-scope topics |

Switch with `PROMPT_VERSION=v1` or `v2`. Run the same questions on both and screenshot the difference.

## 4. Error handling
Empty or over-long input, invalid JSON, greetings/thanks, out-of-scope questions, unclear intent
(low confidence), missing API key, invalid key (401/403), rate limit (429), server errors (5xx),
timeouts and network failure (retries with backoff, then graceful fallback to built-in guidance).
Proof: `python test_chatbot.py`.

## 5. Model results (python evaluate.py)
405 labelled examples (225 starter + 180 added), 15 intents.
Hold-out accuracy about 68%, 5-fold CV about 67%. Confusion matrix in reports/confusion_matrix.png.
Main limit is dataset size; adding more examples per intent is the best way to improve.

## 6. Run it
```
pip install -r requirements.txt
# optional: pick ONE API
set GEMINI_API_KEY=your_key        (Windows CMD)   |  export GEMINI_API_KEY=your_key   (Mac/Linux)
set ANTHROPIC_API_KEY=your_key
python train_model.py              # trains and saves the classifier (also happens automatically)
python app.py                      # open http://127.0.0.1:5000
```
Optional: `GEMINI_MODEL`, `ANTHROPIC_MODEL`, `LLM_PROVIDER=offline|gemini|anthropic`, `PROMPT_VERSION=v1|v2`.

## 7. Files
app.py (Flask) | engine.py (classifier, context, orchestration) | prompts.py | llm_client.py |
knowledge_base.py | evaluate.py | test_chatbot.py | templates/index.html | data/*.csv
