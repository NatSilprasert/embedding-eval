"""
Plot cost vs composite score for a selected set of models.

Pass model keys as CLI arguments to override the default selection:
  python 06_plot_selected_models.py bge-m3 gemini-embedding-001 cohere-embed-v3

Available model keys:
  bge-m3, qwen3-embedding-4b, qwen3-embedding-8b, gemini-embedding-001,
  text-embedding-3-small, text-embedding-3-large, cohere-embed-v3, cohere-embed-v4

Output:
  ./results/plots/eval_results_selected_models.png
"""

import argparse
import glob
import json
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

from config import MODEL_COSTS, RESULTS_DIR, EMBEDDING_DIMS
from config import DOCS as ALL_DOCS_PDF

_ALL_DOCS = [d.replace(".pdf", "") for d in ALL_DOCS_PDF if "mixed" not in d]
_TH_DOCS  = [d for d in _ALL_DOCS if d.endswith("_th")]
_EN_DOCS  = [d for d in _ALL_DOCS if d.endswith("_en")]

PANELS = [
    (_TH_DOCS,  f"Thai ({len(_TH_DOCS)} docs)"),
    (_EN_DOCS,  f"English ({len(_EN_DOCS)} docs)"),
    (_ALL_DOCS, f"Combined ({len(_ALL_DOCS)} docs)"),
]

DEFAULT_MODELS = [
    "qwen3-embedding-8b",
    "qwen3-embedding-4b",
    "gemini-embedding-001",
]

ALL_COLORS = {
    "bge-m3":                 "#10B981",
    "qwen3-embedding-4b":     "#8B5CF6",
    "qwen3-embedding-8b":     "#A855F7",
    "gemini-embedding-001":   "#F59E0B",
    "text-embedding-3-small": "#3B82F6",
    "text-embedding-3-large": "#1D4ED8",
    "cohere-embed-v3":        "#EF4444",
    "cohere-embed-v4":        "#DC2626",
}

ALL_SHORT = {
    "bge-m3":                 "BGE-M3",
    "qwen3-embedding-4b":     "Qwen3-4B",
    "qwen3-embedding-8b":     "Qwen3-8B",
    "gemini-embedding-001":   "Gemini-001",
    "text-embedding-3-small": "OAI-Small",
    "text-embedding-3-large": "OAI-Large",
    "cohere-embed-v3":        "Cohere-v3",
    "cohere-embed-v4":        "Cohere-v4",
}

# Y_LIM and X_LIM computed dynamically from data in main()


def load_scores(doc_list: list, selected_models: list) -> dict:
    """Average composite_score across all strategies and given docs per selected model."""
    scores = {}
    for model in selected_models:
        vals = []
        for doc in doc_list:
            for fp in glob.glob(f"{RESULTS_DIR}/{model}_*_{doc}.json"):
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                vals.extend(r["composite_score"] for r in data if "composite_score" in r)
        if vals:
            scores[model] = float(np.mean(vals))
    return scores


def draw(ax, scores: dict, title: str, selected_models: list, xlim: tuple, ylim: tuple):
    if not scores:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color="#9CA3AF", fontsize=11)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        return

    xs = [MODEL_COSTS[m] for m in scores]
    ys = [scores[m] for m in scores]

    ax.axvline(np.median(xs), color="#E5E7EB", lw=1, ls="--", zorder=1)
    ax.axhline(np.median(ys), color="#E5E7EB", lw=1, ls="--", zorder=1)

    for model in selected_models:
        if model not in scores:
            continue
        x = MODEL_COSTS[model]
        y = scores[model]
        ax.scatter(x, y, s=140, color=ALL_COLORS.get(model, "#6B7280"),
                   edgecolors="white", linewidths=1.2, zorder=5)
        ax.annotate(
            f"{ALL_SHORT.get(model, model)}\n{y:.3f}",
            xy=(x, y), xytext=(6, 6), textcoords="offset points",
            fontsize=9, color="#111827", zorder=6, clip_on=True,
        )

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel("Cost / 1M tokens (USD)", fontsize=10)
    ax.set_ylabel("Composite score", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=4)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25, lw=0.5)
    ax.tick_params(labelsize=9)


def parse_args():
    valid = list(EMBEDDING_DIMS.keys())
    parser = argparse.ArgumentParser(
        description="Plot cost vs composite score for selected embedding models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available models:\n  " + "\n  ".join(valid),
    )
    parser.add_argument(
        "models", nargs="*",
        help="Model keys to plot (default: qwen3-embedding-8b qwen3-embedding-4b gemini-embedding-001)",
    )
    args = parser.parse_args()

    if args.models:
        unknown = [m for m in args.models if m not in valid]
        if unknown:
            print(f"Unknown model(s): {unknown}\nAvailable: {valid}", file=sys.stderr)
            sys.exit(1)
        return args.models
    return DEFAULT_MODELS


def main():
    selected_models = parse_args()

    os.makedirs(f"{RESULTS_DIR}/plots", exist_ok=True)
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})

    # Load all panels first to compute shared axes
    panel_data = [(load_scores(doc_list, selected_models), title) for doc_list, title in PANELS]

    all_vals = [v for scores, _ in panel_data for v in scores.values()]
    all_costs = [MODEL_COSTS[m] for m in selected_models if m in MODEL_COSTS]

    if all_vals:
        y_span   = max(all_vals) - min(all_vals) or 0.05
        y_margin = y_span * 0.20
        y_lim    = (max(0.0, min(all_vals) - y_margin), min(1.0, max(all_vals) + y_margin))
    else:
        y_lim = (0.0, 1.0)

    if all_costs:
        x_span   = max(all_costs) - min(all_costs) or 0.01
        x_margin = x_span * 0.25
        x_lim    = (max(0.0, min(all_costs) - x_margin), max(all_costs) + x_margin)
    else:
        x_lim = (0.0, 0.20)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    model_label = ", ".join(ALL_SHORT.get(m, m) for m in selected_models)
    fig.suptitle(f"Selected models — Cost vs Composite Score\n{model_label}",
                 fontsize=12, fontweight="bold")

    for ax, (scores, title) in zip(axes, panel_data):
        draw(ax, scores, title, selected_models, x_lim, y_lim)

    handles = [
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=ALL_COLORS.get(m, "#6B7280"),
                   markeredgecolor="white", markersize=9,
                   label=ALL_SHORT.get(m, m))
        for m in selected_models
    ]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles),
               bbox_to_anchor=(0.5, 0.01), frameon=False, fontsize=10)

    fig.tight_layout(rect=[0, 0.08, 1, 0.94])
    out = f"{RESULTS_DIR}/plots/eval_results_selected_models.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()

