import json

def combine_json_files(input_file1, input_file2):
    # Load the JSON data from both input files
    with open(input_file1, 'r', encoding='utf-8') as file1:
        data1 = json.load(file1)
        
    with open(input_file2, 'r', encoding='utf-8') as file2:
        data2 = json.load(file2)
    
    # Combine the data
    combined_data = {**data1, **data2}
    
    # Return the combined data as a dictionary
    return combined_data

# Example usage
input_file1 = 'output1.json'
input_file2 = 'output2.json'

combined_data = combine_json_files(input_file1, input_file2)

# Now you can use `combined_data` as a dictionary
top_10_items = dict(list(combined_data.items())[:10])
print(json.dumps(top_10_items, indent=4))
