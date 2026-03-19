"""
Scatter plot: cost (USD/1M tokens) vs composite score.
Layout: 1×3 — Thai docs avg | English docs avg | Combined (all 18 docs, excl. mixed)

All panels share the same y-axis scale, computed from actual data.
Saves to ./results/plots/eval_results_combined.png
"""
import os, json, glob, random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from config import MODEL_COSTS, RESULTS_DIR, DOCS as ALL_DOCS_PDF

PLOT_DIR = f"{RESULTS_DIR}/plots"

# All docs excluding mixed, split by language
ALL_DOCS = [d.replace(".pdf", "") for d in ALL_DOCS_PDF if "mixed" not in d]
TH_DOCS  = [d for d in ALL_DOCS if d.endswith("_th")]
EN_DOCS  = [d for d in ALL_DOCS if d.endswith("_en")]

PANELS = [
    (TH_DOCS,  f"Thai ({len(TH_DOCS)} docs)"),
    (EN_DOCS,  f"English ({len(EN_DOCS)} docs)"),
    (ALL_DOCS, f"Combined ({len(ALL_DOCS)} docs)"),
]

COLORS = {
    "bge-m3":                 "#06B6D4",
    "qwen3-embedding-4b":     "#8B5CF6",
    "qwen3-embedding-8b":     "#A855F7",
    "gemini-embedding-001":   "#F59E0B",
    "text-embedding-3-small": "#3B82F6",
    "text-embedding-3-large": "#1D4ED8",
    "cohere-embed-v3":        "#EF4444",
    "cohere-embed-v4":        "#B91C1C",
}

PROVIDER_GROUP = {
    "bge-m3":                 "Open-source",
    "qwen3-embedding-4b":     "Open-source",
    "qwen3-embedding-8b":     "Open-source",
    "gemini-embedding-001":   "Google",
    "text-embedding-3-small": "OpenAI",
    "text-embedding-3-large": "OpenAI",
    "cohere-embed-v3":        "Cohere",
    "cohere-embed-v4":        "Cohere",
}

SHORT_NAMES = {
    "bge-m3":                 "BGE-M3",
    "qwen3-embedding-4b":     "Qwen3-4B",
    "qwen3-embedding-8b":     "Qwen3-8B",
    "gemini-embedding-001":   "Gem-001",
    "text-embedding-3-small": "OAI-Small",
    "text-embedding-3-large": "OAI-Large",
    "cohere-embed-v3":        "Cohere-v3",
    "cohere-embed-v4":        "Cohere-v4",
}


def load_scores(doc_list: list) -> dict:
    """Average composite_score across all strategies and given docs per model."""
    scores = {}
    for model in MODEL_COSTS:
        vals = []
        for doc in doc_list:
            for fp in glob.glob(f"{RESULTS_DIR}/{model}_*_{doc}.json"):
                with open(fp) as f:
                    data = json.load(f)
                vals.extend(r["composite_score"] for r in data if "composite_score" in r)
        if vals:
            scores[model] = float(np.mean(vals))
    return scores


def draw_scatter(ax, scores: dict, title: str, ylim: tuple):
    if not scores:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color="#9CA3AF", fontsize=11)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylim(*ylim)
        return

    costs = [MODEL_COSTS[m] for m in scores]
    vals  = list(scores.values())

    ax.axvline(np.median(costs), color="#E5E7EB", lw=1, ls="--", zorder=1)
    ax.axhline(np.median(vals),  color="#E5E7EB", lw=1, ls="--", zorder=1)

    q_kw = dict(fontsize=7, color="#D1D5DB", style="italic",
                ha="center", va="center", transform=ax.transAxes, zorder=2)
    ax.text(0.18, 0.88, "Best value",  **q_kw)
    ax.text(0.82, 0.88, "Premium",     **q_kw)
    ax.text(0.18, 0.12, "Low / cheap", **q_kw)
    ax.text(0.82, 0.12, "Overpriced",  **q_kw)

    random.seed(42)
    for model, score in sorted(scores.items(), key=lambda kv: MODEL_COSTS[kv[0]]):
        cost = MODEL_COSTS[model]
        if cost == 0.0:
            cost += random.uniform(0.001, 0.003)
        ax.scatter(cost, score, s=110, color=COLORS.get(model, "#6B7280"),
                   zorder=5, edgecolors="white", linewidths=1.2)
        ax.annotate(
            f"{SHORT_NAMES.get(model, model)}\n{score:.3f}",
            xy=(cost, score), xytext=(5, 6), textcoords="offset points",
            fontsize=7, color="#111827", zorder=6, clip_on=True,
        )

    ax.set_xlim(left=max(0, min(costs) - 0.005))
    ax.set_ylim(*ylim)
    ax.set_xlabel("Cost / 1M tokens (USD)", fontsize=9)
    ax.set_ylabel("Composite score", fontsize=9)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax.tick_params(labelsize=8)


def main():
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})

    # Load all panels first to compute shared y scale
    panel_data = [(load_scores(docs), title) for docs, title in PANELS]

    all_vals = [v for scores, _ in panel_data for v in scores.values()]
    if all_vals:
        span   = max(all_vals) - min(all_vals) or 0.05
        margin = span * 0.15
        ylim   = (max(0.0, min(all_vals) - margin), min(1.0, max(all_vals) + margin))
    else:
        ylim = (0.0, 1.0)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("RAG Evaluation — Cost vs Composite Score (all docs, excl. mixed)",
                 fontsize=13, fontweight="bold")

    for ax, (scores, title) in zip(axes, panel_data):
        draw_scatter(ax, scores, title, ylim)

    # Legend
    seen: dict = {}
    for scores, _ in panel_data:
        for model in scores:
            g = PROVIDER_GROUP.get(model, "Other")
            if g not in seen:
                seen[g] = COLORS.get(model, "#6B7280")
    handles = [mpatches.Patch(color=c, label=lbl) for lbl, c in seen.items()]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles),
               fontsize=9, bbox_to_anchor=(0.5, 0.0), frameon=False)

    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    out = f"{PLOT_DIR}/eval_results_combined.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.1)
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
