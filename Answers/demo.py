import json

# Function to read JSON file and count the length of the JSON
def count_json_length(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return len(json_data)

# Path to the JSON file
file_path = 'Answers/solutions.json'

# Count the length of the JSON
json_length = count_json_length(file_path)
print(f"The length of the JSON is: {json_length}")
