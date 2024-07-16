import json

input_file_path = r'C:\Users\kodem\OneDrive\Desktop\exam\KODEMAPA-EXAMPAD\Answers\solutions.json'  # Replace with your JSON file path
output_file_path = 'min-solutions.json'  # Replace with the output file path

# Read the JSON file
with open(input_file_path, 'r', encoding='utf-8') as input_file:
    data = json.load(input_file)

# Write the minified JSON to the output file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(data, output_file, separators=(',', ':'))

print(f"Minified JSON file saved to: {output_file_path}")
