import pickle

# Specify the path to your pickle file
pickle_file_path = "/home/jahangir/Downloads/python_model.pkl"

# Open the file in binary read mode
with open(pickle_file_path, "rb") as file:
    # Load the data from the pickle file
    data = pickle.load(file)

# Use the loaded data
print(data)
