import json

def load_solutions(filename='Answers/solutions.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: File {filename} contains invalid JSON.")
        return {}

def get_answers(question_ids, solutions_file='Answers/solutions.json'):
    solutions = load_solutions(solutions_file)
    if not solutions:
        return {}

    results = {}
    for qid in question_ids:
        if qid in solutions:
            results[qid] = {
                'correct_answers': solutions[qid]['correct_answers'],
                'explanation': solutions[qid]['explanation']
            }
        else:
            results[qid] = {
                'correct_answers': None,
                'explanation': 'Question ID not found in solutions.'
            }
    return results

# Example usage
if __name__ == "__main__":
    # This is just for demonstration
    example_ids = ['091a5a31a1d0404398582d23784a2dee', '93faed2a5f8a474ba39bee261519df38']
    answers = get_answers(example_ids)
    print(json.dumps(answers, indent=2, ensure_ascii=False))