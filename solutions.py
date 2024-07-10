import json
import os

def process_json(input_data):
    result = {}
    for question in input_data['result']['data']['sec_questions']:
        qid = question[12]
        correct_answers = question[4]
        explanation = question[6]
        
        result[qid] = {
            'correct_answers': correct_answers,
            'explanation': explanation
        }
    
    return result

def update_json_file(new_data, filename):
    existing_data = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    existing_data = json.loads(content)
                else:
                    print(f"Warning: {filename} is empty. Starting with a new dictionary.")
        except json.JSONDecodeError:
            print(f"Warning: {filename} contains invalid JSON. Starting with a new dictionary.")
    else:
        print(f"Info: {filename} does not exist. Creating a new file.")

    existing_data.update(new_data)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def main(input_filename):
    try:
        # Read the input JSON file
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                raise ValueError(f"Input file {input_filename} is empty")
            input_data = json.loads(content)
        
        # Process the data
        processed_data = process_json(input_data)
        
        output_filename = 'Answers/solutions.json'
        # Update the JSON file
        update_json_file(processed_data, output_filename)
        
        print(f"Data from {input_filename} processed and {output_filename} updated successfully.")
    except FileNotFoundError:
        print(f"Error: Input file {input_filename} not found.")
    except json.JSONDecodeError:
        print(f"Error: Input file {input_filename} contains invalid JSON.")
    except KeyError as e:
        print(f"Error: Expected key not found in input JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    input_fileName = r"C:\Users\pavan\OneDrive\Desktop\km_sol_Json\km_sol_Json\PhysicsXII.json"
    main(input_fileName)