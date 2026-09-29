import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
IMG_DIR = ROOT / "docs" / "images"


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(DATA_DIR / "message_manifest.csv")
    counts = manifest["trigger"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(counts.index, counts.values, color="#06A77D")
    ax.set_title("Synthetic ADT Message Triggers (HL7 v2 Lab)")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "adt_trigger_counts.png", dpi=120)
    plt.close(fig)

    # Round-trip success from output if present
    summary_path = ROOT / "output" / "roundtrip_summary.json"
    if summary_path.exists():
        import json

        data = json.loads(summary_path.read_text(encoding="utf-8"))
        df = pd.DataFrame(data)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["patient_id_match", "visit_match"], [df["patient_id_match"].mean(), df["visit_match"].mean()])
        ax.set_ylim(0, 1.05)
        ax.set_title("FHIR Round-Trip Field Match Rate (First N Messages)")
        fig.tight_layout()
        fig.savefig(IMG_DIR / "roundtrip_match_rates.png", dpi=120)
        plt.close(fig)
    print(f"Charts saved to {IMG_DIR}")


if __name__ == "__main__":
    main()
