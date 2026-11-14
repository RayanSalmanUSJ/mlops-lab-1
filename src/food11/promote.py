import argparse
import math

from mlflow.tracking import MlflowClient


def promote(candidate_version: int):
    client = MlflowClient()
    n = 1000  # Number of images in our evaluation set
    model_name = "food11"
    
    # 1. Get Candidate metrics
    candidate = client.get_model_version(model_name, candidate_version)
    cand_run = client.get_run(candidate.run_id)
    acc_candidate = cand_run.data.metrics.get("val_accuracy", 0.0)
    
    # 2. Get Champion metrics
    try:
        champion = client.get_model_version_by_alias(model_name, "champion")
        champ_run = client.get_run(champion.run_id)
        acc_champion = champ_run.data.metrics.get("val_accuracy", 0.0)
    except Exception: # noqa: BLE001
        # If no champion exists, auto-promote the first one
        client.set_registered_model_alias(model_name, "champion", candidate_version)
        print(f"No existing champion. Version {candidate_version} promoted.")
        return

    # 3. Calculate Standard Error bounds
    p = acc_champion
    se = math.sqrt(p * (1 - p) / n)
    
    # 4. Gate Logic
    if acc_candidate >= acc_champion + 2 * se:
        client.set_registered_model_alias(model_name, "champion", candidate_version)
        decision = "Promoted to Champion"
    else:
        client.set_registered_model_alias(model_name, "challenger", candidate_version)
        decision = "Demoted to Challenger"
        
    # 5. Tagging the decision
    client.set_model_version_tag(model_name, candidate_version, "gate_decision", decision)
    client.set_model_version_tag(model_name, candidate_version, "acc_candidate", f"{acc_candidate:.4f}")
    client.set_model_version_tag(model_name, candidate_version, "acc_champion", f"{acc_champion:.4f}")
    print(f"Gate decision: {decision}. Cand: {acc_candidate:.4f}, Champ: {acc_champion:.4f}, SE: {se:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()
    promote(args.version)