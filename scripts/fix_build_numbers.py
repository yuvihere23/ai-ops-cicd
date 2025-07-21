import json

DATASET_PATH = "dataset/dataset.json"

def fix_build_numbers():
    try:
        with open(DATASET_PATH, "r") as f:
            data = json.load(f)

        # Sort by run_id for logical consistency
        data.sort(key=lambda x: x.get("run_id", 0))

        # Assign new sequential build numbers
        for i, entry in enumerate(data, start=1):
            entry["build_number"] = i

        # Save back to file
        with open(DATASET_PATH, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Successfully reassigned build numbers for {len(data)} entries.")
    
    except FileNotFoundError:
        print("❌ dataset.json not found.")
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    fix_build_numbers()
