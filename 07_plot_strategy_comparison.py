"""
Grouped bar chart: composite_score per model, split by chunking strategy.

Rows:  Thai docs avg | English docs avg | All docs avg (excl. mixed)
Each row: one horizontal grouped-bar per model, 4 bars = 4 strategies.
All rows share the same x-axis scale.

Saves to ./results/plots/plot_strategy_comparison.png
"""
import os, json, glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from config import RESULTS_DIR, DOCS as ALL_DOCS_PDF

STRATEGIES = ["token_512", "sliding_512", "token_500_ov50", "token_256_ov32"]
STRATEGY_LABELS = {
    "token_512":       "token-512",
    "sliding_512":     "sliding-512",
    "token_500_ov50":  "token-500 ov50",
    "token_256_ov32":  "token-256 ov32",
}
STRATEGY_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

ALL_DOCS = [d.replace(".pdf", "") for d in ALL_DOCS_PDF if "mixed" not in d]
TH_DOCS  = [d for d in ALL_DOCS if d.endswith("_th")]
EN_DOCS  = [d for d in ALL_DOCS if d.endswith("_en")]

GROUPS = [
    (TH_DOCS,  f"Thai ({len(TH_DOCS)} docs)"),
    (EN_DOCS,  f"English ({len(EN_DOCS)} docs)"),
    (ALL_DOCS, f"All ({len(ALL_DOCS)} docs)"),
]


def load_scores() -> dict:
    """scores[group_name][model][strategy] = mean composite_score"""
    scores = {title: {} for _, title in GROUPS}

    for path in glob.glob(os.path.join(RESULTS_DIR, "*.json")):
        fname    = os.path.basename(path).replace(".json", "")
        doc      = next((d for d in ALL_DOCS if fname.endswith(f"_{d}")), None)
        if not doc:
            continue
        prefix   = fname[:-(len(doc) + 1)]
        strategy = next((s for s in STRATEGIES if prefix.endswith(f"_{s}")), None)
        if not strategy:
            continue
        model = prefix[:-(len(strategy) + 1)]

        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
        vals = [float(r["composite_score"]) for r in rows if "composite_score" in r]
        if not vals:
            continue

        for doc_list, title in GROUPS:
            if doc in doc_list:
                scores[title].setdefault(model, {}).setdefault(strategy, []).extend(vals)

    # Average down to single float
    result = {}
    for title in scores:
        result[title] = {}
        for model, strat_vals in scores[title].items():
            result[title][model] = {
                s: float(np.mean(v)) for s, v in strat_vals.items() if v
            }
    return result


def draw_group(ax, model_scores: dict, title: str, xlim: tuple):
    """Horizontal grouped bar chart: models on y, grouped bars per strategy."""
    # Sort models by avg across all strategies (best at top)
    model_avgs = {
        m: np.mean(list(sv.values()))
        for m, sv in model_scores.items() if sv
    }
    models = sorted(model_avgs, key=model_avgs.get, reverse=False)  # ascending → best at top

    n_models    = len(models)
    n_strategies = len(STRATEGIES)
    bar_h = 0.18
    group_gap = 0.15

    for si, strategy in enumerate(STRATEGIES):
        offsets = np.arange(n_models) * (n_strategies * bar_h + group_gap)
        y_pos   = offsets + si * bar_h
        values  = [model_scores.get(m, {}).get(strategy, 0.0) for m in models]
        ax.barh(y_pos, values, height=bar_h,
                color=STRATEGY_COLORS[si], alpha=0.85,
                label=STRATEGY_LABELS[strategy])
        for yp, v in zip(y_pos, values):
            if v > 0:
                ax.text(v + (xlim[1] - xlim[0]) * 0.005, yp,
                        f"{v:.3f}", va="center", fontsize=6.5, clip_on=True)

    # y-tick at center of each model group
    center_offsets = np.arange(n_models) * (n_strategies * bar_h + group_gap) \
                     + (n_strategies - 1) * bar_h / 2
    ax.set_yticks(center_offsets)
    ax.set_yticklabels(models, fontsize=8)
    ax.set_xlim(*xlim)
    ax.set_xlabel("Composite score", fontsize=9)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, lw=0.5)


def main():
    os.makedirs(f"{RESULTS_DIR}/plots", exist_ok=True)
    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})

    scores = load_scores()

    # Compute shared x scale from all values
    all_vals = [
        v
        for group_scores in scores.values()
        for strat_vals in group_scores.values()
        for v in strat_vals.values()
    ]
    if all_vals:
        span = max(all_vals) - min(all_vals) or 0.05
        xlim = (max(0.0, min(all_vals) - span * 0.05),
                min(1.0, max(all_vals) + span * 0.12))
    else:
        xlim = (0.0, 1.0)

    n_models = max(len(v) for v in scores.values()) if scores else 8
    n_strategies = len(STRATEGIES)
    bar_h = 0.18
    group_gap = 0.15
    fig_h = max(4.0, n_models * (n_strategies * bar_h + group_gap) + 1.5)

    fig, axes = plt.subplots(1, 3, figsize=(20, fig_h))
    fig.suptitle("Composite Score by Chunking Strategy",
                 fontsize=13, fontweight="bold")

    for ax, (_, title) in zip(axes, GROUPS):
        draw_group(ax, scores.get(title, {}), title, xlim)

    # Shared legend
    handles = [mpatches.Patch(color=STRATEGY_COLORS[i],
                              label=STRATEGY_LABELS[s])
               for i, s in enumerate(STRATEGIES)]
    fig.legend(handles=handles, loc="lower center", ncol=len(STRATEGIES),
               fontsize=9, bbox_to_anchor=(0.5, 0.0), frameon=False)

    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    out = f"{RESULTS_DIR}/plots/plot_strategy_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.1)
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
