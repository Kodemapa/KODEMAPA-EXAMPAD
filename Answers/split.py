import json

def split_json_file(input_file, output_file1, output_file2):
    # Load the JSON data from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Get the list of keys
    keys = list(data.keys())
    
    # Split the keys into two halves
    mid_index = len(keys) // 2
    keys1 = keys[:mid_index]
    keys2 = keys[mid_index:]
    
    # Create two new dictionaries for each half
    data1 = {key: data[key] for key in keys1}
    data2 = {key: data[key] for key in keys2}
    
    # Save each half into separate files
    with open(output_file1, 'w', encoding='utf-8') as file1:
        json.dump(data1, file1, indent=4)
        
    with open(output_file2, 'w', encoding='utf-8') as file2:
        json.dump(data2, file2, indent=4)

# Example usage
input_file = r"C:\Users\kodem\OneDrive\Desktop\exam\KODEMAPA-EXAMPAD\Answers\solutions2.json"
output_file1 = 'output1.json'
output_file2 = 'output2.json'

split_json_file(input_file, output_file1, output_file2)
