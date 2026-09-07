import numpy as np

data = np.load("model/awareness_fork_gru_test.norm.npz", allow_pickle=True)
print("Keys:", data.files)
print("Mean:", data["mean"])
print("Std:", data["std"])
print("Feature columns:", data["feature_cols"])