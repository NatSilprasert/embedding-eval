"""
Bar charts for multiple metrics.

Rows:  Thai docs avg | English docs avg | All docs avg (excl. mixed)
Cols:  token_512 | sliding_512 | token_500_ov50 | token_256_ov32 | avg (all strategies)

All subplots in the same figure share the same x-axis scale.
Saves one PNG per metric to ./results/plots/
"""
import os, json, glob
import numpy as np
import matplotlib.pyplot as plt
from config import RESULTS_DIR, DOCS as ALL_DOCS_PDF

STRATEGIES = ["token_512", "sliding_512", "token_500_ov50", "token_256_ov32"]
METRICS    = [
    "composite_score",
    "recall_at_5",
    "mrr",
    "ndcg_at_5",
    "answer_similarity",
    "cross_lingual_score",
]

# All docs excluding mixed, grouped by language
ALL_DOCS = [d.replace(".pdf", "") for d in ALL_DOCS_PDF if "mixed" not in d]
TH_DOCS  = [d for d in ALL_DOCS if d.endswith("_th")]
EN_DOCS  = [d for d in ALL_DOCS if d.endswith("_en")]

LANG_GROUPS = {
    f"Thai ({len(TH_DOCS)} docs)":    TH_DOCS,
    f"English ({len(EN_DOCS)} docs)": EN_DOCS,
    f"All ({len(ALL_DOCS)} docs)":    ALL_DOCS,
}


def load_results(metric: str) -> dict:
    """stats[group_name][(model, strategy)] = [values...]"""
    stats = {name: {} for name in LANG_GROUPS}

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
        vals = [float(r[metric]) for r in rows if r.get(metric) is not None]
        if not vals:
            continue

        key = (model, strategy)
        for group_name, group_docs in LANG_GROUPS.items():
            if doc in group_docs:
                stats[group_name].setdefault(key, []).extend(vals)

    return stats


def aggregate_by_model_strategy(stats: dict) -> dict:
    """agg[group][(model, strategy)] = {"mean": float, "std": float}"""
    agg = {}
    for group, combos in stats.items():
        rows = []
        for (model, strategy), vals in combos.items():
            if not vals:
                continue
            arr = np.array(vals, dtype=float)
            rows.append({"model": model, "strategy": strategy,
                         "mean": float(arr.mean()), "std": float(arr.std(ddof=0))})
        rows.sort(key=lambda r: r["mean"], reverse=True)
        agg[group] = rows
    return agg


def aggregate_by_model(stats: dict) -> dict:
    """agg_model[group][model] = {"mean": float, "std": float} avg across strategies"""
    agg = {}
    for group, combos in stats.items():
        by_model: dict = {}
        for (model, strategy), vals in combos.items():
            if not vals:
                continue
            by_model.setdefault(model, []).append(float(np.mean(vals)))
        rows = []
        for model, means in by_model.items():
            arr = np.array(means, dtype=float)
            rows.append({"model": model, "mean": float(arr.mean()),
                         "std": float(arr.std(ddof=0)) if len(arr) > 1 else 0.0})
        rows.sort(key=lambda r: r["mean"], reverse=True)
        agg[group] = rows
    return agg


def _draw_hbar(ax, rows: list, xlim: tuple, color: str, metric: str, top_n: int = 10):
    rows = rows[:top_n]
    if not rows:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color="gray", fontsize=9)
        ax.set_yticks([])
        return

    means  = [r["mean"] for r in rows]
    stds   = [r["std"]  for r in rows]
    labels = [r["model"] for r in rows]
    y = np.arange(len(rows))

    ax.barh(y, means, xerr=stds, capsize=2, color=color, alpha=0.85)
    xlo, xhi = xlim
    offset = (xhi - xlo) * 0.01
    for yi, m in zip(y, means):
        ax.text(min(m + offset, xhi - offset * 2), yi,
                f"{m:.3f}", va="center", fontsize=7, clip_on=True)

    ax.set_xlim(*xlim)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel(metric, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3, lw=0.5)


def plot_metric(agg, agg_model, metric: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    group_names = list(LANG_GROUPS.keys())
    col_strategies = STRATEGIES  # 4 strategy cols
    TOP_N = 10

    # Collect all means → shared x scale
    all_means = []
    for group in group_names:
        for s in col_strategies:
            all_means.extend(r["mean"] for r in agg[group] if r["strategy"] == s)
        all_means.extend(r["mean"] for r in agg_model[group])
    if all_means:
        span   = max(all_means) - min(all_means) or 0.05
        xmin   = max(0.0, min(all_means) - span * 0.08)
        xmax   = min(1.0, max(all_means) + span * 0.15)
    else:
        xmin, xmax = 0.0, 1.0
    shared_xlim = (xmin, xmax)

    ncols   = len(col_strategies) + 1   # +1 for avg column
    nrows   = len(group_names)
    max_bars = max(
        (len([r for r in agg[g] if r["strategy"] == s][:TOP_N])
         if s is not None else len(agg_model[g][:TOP_N]))
        for g in group_names
        for s in list(col_strategies) + [None]
    )
    row_h = max(3.0, max_bars * 0.38)

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, row_h * nrows))
    if nrows == 1:
        axes = axes[np.newaxis, :]

    col_titles = list(col_strategies) + ["avg (all strategies)"]
    col_colors = ["#4C72B0"] * len(col_strategies) + ["#55A868"]

    for ci, title in enumerate(col_titles):
        axes[0, ci].set_title(title, fontsize=10, fontweight="bold", pad=6)

    for ri, group in enumerate(group_names):
        axes[ri, 0].set_ylabel(group, fontsize=9, labelpad=4)
        for ci, strategy in enumerate(col_strategies):
            rows = [r for r in agg[group] if r["strategy"] == strategy][:TOP_N]
            _draw_hbar(axes[ri, ci], rows, shared_xlim, col_colors[ci], metric)
        # Avg column
        _draw_hbar(axes[ri, -1], agg_model[group][:TOP_N],
                   shared_xlim, col_colors[-1], metric)

    fig.suptitle(metric, fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    out = os.path.join(out_dir, f"plot_{metric}.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"Saved {out}")


def main():
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    plot_dir = os.path.join(RESULTS_DIR, "plots")

    for metric in METRICS:
        print(f"=== {metric} ===")
        stats     = load_results(metric)
        agg       = aggregate_by_model_strategy(stats)
        agg_model = aggregate_by_model(stats)
        plot_metric(agg, agg_model, metric, plot_dir)


if __name__ == "__main__":
    main()
