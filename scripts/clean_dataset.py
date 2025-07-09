import os

folder = "dataset"

if os.path.exists(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print(f"[OK] Cleaned all files in {folder}/")
else:
    print("[INFO] dataset/ folder not found. Creating new one.")
    os.makedirs(folder)
