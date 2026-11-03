"""Model evaluation for the report: python evaluate.py"""
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from engine import DATA_PATH, build_pipeline, detect_context, context_to_text

df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
X_tr, X_te, y_tr, y_te = train_test_split(df["text"], df["intent"], test_size=0.2,
                                          stratify=df["intent"], random_state=42)
model = build_pipeline().fit(X_tr, y_tr)
pred = model.predict(X_te)
acc = accuracy_score(y_te, pred)
cv = cross_val_score(build_pipeline(), df["text"], df["intent"],
                     cv=StratifiedKFold(5, shuffle=True, random_state=42))
report = classification_report(y_te, pred, zero_division=0)

lines = [f"Samples: {len(df)} | Intents: {df['intent'].nunique()}",
         f"Hold-out accuracy (80/20): {acc:.2%}",
         f"5-fold CV accuracy: {cv.mean():.2%} (+/- {cv.std():.2%})", "", report]

lines.append("Context detection examples:")
for t in ["I'm shooting an Indian hip-hop music video at night with one artist, a parking lot and a car. Dark and aggressive.",
          "How can I light an interview with one LED on a low budget?",
          "I want my reel to feel nostalgic"]:
    lines.append(f"  {t[:70]} -> {context_to_text(detect_context(t))}")
out = "\n".join(lines)
print(out)
open("reports/metrics.txt", "w", encoding="utf-8").write(out)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = sorted(df["intent"].unique())
    cm = confusion_matrix(y_te, pred, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels, rotation=90, fontsize=8)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.set_title("TVASTR intent classifier - confusion matrix")
    for i in range(len(labels)):
        for j in range(len(labels)):
            if cm[i, j]:
                ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8)
    plt.tight_layout()
    plt.savefig("reports/confusion_matrix.png", dpi=150)
    print("\nSaved reports/confusion_matrix.png")
except ImportError:
    print("\n(matplotlib not installed - skipped confusion matrix)")
