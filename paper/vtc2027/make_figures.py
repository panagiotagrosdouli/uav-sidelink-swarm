"""Generate the three figures used by the VTC2027-Spring draft.

The CSV inputs are compact, audited extracts from paper-operating-envelope
workflow run #26 on scientific commit f224ba9e5f95a23a088db24479c67461fcf497e6.
They are publication evidence summaries, not independent measurements.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)


def save(fig, stem):
    fig.tight_layout()
    fig.savefig(FIGS / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIGS / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def topology_resources():
    df = pd.read_csv(DATA / "topology_resources.csv")
    fig, ax = plt.subplots(figsize=(5.1, 3.1))
    for pairing, group in df.groupby("pairing"):
        group = group.sort_values("n_resources")
        label = "greedy short-link" if pairing == "nearest_neighbor" else "sequential"
        ax.plot(group.n_resources, group.mean_first_tx_success, marker="o", label=label)
    ax.set_xlabel("Orthogonal frequency resources, R")
    ax.set_ylabel("Mean first-TX success")
    ax.set_xticks([1, 4, 8])
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    save(fig, "topology_sensitivity")


def topology_scaling():
    df = pd.read_csv(DATA / "topology_scaling.csv")
    fig, ax = plt.subplots(figsize=(5.1, 3.1))
    for pairing, group in df.groupby("pairing"):
        group = group.sort_values("n_uavs")
        label = "greedy short-link" if pairing == "nearest_neighbor" else "sequential"
        ax.plot(group.n_uavs, group.mean_first_tx_success, marker="o", label=label)
    ax.set_xlabel("UAVs, N")
    ax.set_ylabel("Mean first-TX success")
    ax.set_xticks([20, 50, 100])
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    save(fig, "topology_scaling")


def operating_envelope():
    df = pd.read_csv(DATA / "operating_envelope.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for g, group in df.groupby("directional_relative_advantage_db"):
        group = group.sort_values("n_resources")
        ax.plot(group.n_resources, group.max_evaluated_n_meeting_both_targets, marker="o", label=f"G={g:g} dB")
    ax.set_xlabel("Orthogonal frequency resources")
    ax.set_ylabel("Max evaluated N meeting both policy targets")
    ax.set_title("Operating envelope: success >= 0.10, goodput >= 1.0 Mbps")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, "operating_envelope")


if __name__ == "__main__":
    topology_resources()
    topology_scaling()
    operating_envelope()
