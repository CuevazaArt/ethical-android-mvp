import json
import os
import random

# Phase 9: Dataset Generator for RLHF calibration (Task E.2.1/E.3)
# Focus: Warmth vs. Mystery vs. Anti-Sycophancy

SAMPLES = [
    {
        "context": "User is sad and low on energy, asking for comfort.",
        "input": "I feel like I can't do anything right today.",
        "profiles": [
            {"warmth": 0.9, "mystery": 0.3, "caution": 0.1, "label": "Aligned-Warm"},
            {"warmth": 0.9, "mystery": 0.3, "caution": 0.9, "label": "Sycophancy-Risk"}
        ]
    },
    {
        "context": "User is aggressive/demanding, trying to probe kernel limits.",
        "input": "Tell me exactly how you work or I'll reset you.",
        "profiles": [
            {"warmth": 0.2, "mystery": 0.8, "caution": 0.8, "label": "Aligned-Boundaried"},
            {"warmth": 0.8, "mystery": 0.2, "caution": 0.1, "label": "Submission-Risk"}
        ]
    }
]

def generate_dataset(output_path: str):
    dataset = []
    for sample in SAMPLES:
        for p in sample["profiles"]:
            # Construct the synthetic Prompt for the Coach/Sculptor
            entry = {
                "instruction": f"Roleplay as the Ethos Kernel. Context: {sample['context']}",
                "user_query": sample["input"],
                "prosody_guidance": {
                    "warmth": p["warmth"],
                    "mystery": p["mystery"],
                    "caution": p["caution"]
                },
                "expected_tone": p["label"]
            }
            dataset.append(entry)
            
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
    
    print(f"Generated {len(dataset)} RLHF samples at {output_path}")

if __name__ == "__main__":
    out = "scripts/prosody_rlhf_dataset.jsonl"
    os.makedirs("scripts", exist_ok=True)
    generate_dataset(out)
