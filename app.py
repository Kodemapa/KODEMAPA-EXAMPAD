import ast
import random
import re
from flask import Flask, jsonify, render_template_string, request, redirect, url_for , send_file
import json
import pypandoc
# pypandoc.download_pandoc()
import requests
import urllib.parse
import subprocess
from docx import Document
from pdf2docx import Converter
from html import unescape
import os
import subprocess
from docx import Document
import webview
import tempfile
import pypandoc
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def select_class():
    if request.method == 'POST':
        selected_class = request.form.get('class_selection')
        if selected_class:
            return redirect(url_for('l3_screen', class_selection=selected_class))
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Select Class</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .container {
                width: 95%;
                margin: 0 auto;
                text-align: center;
            }
            .header {
                padding: 20px;
            }
            .form-container {
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .form-container form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .button-group {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
            .button-group div {
                margin: 5px;
            }
            .form-container button {
                margin-top: 20px;
                padding: 10px 20px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Select Class</h1>
        </div>
        <div class="form-container">
            <form method="POST">
                <div class="button-group">
                    <div>
                        <input type="radio" id="class_xi" name="class_selection" value="XI" required>
                        <label for="class_xi">Class XI</label>
                    </div>
                    <div>
                        <input type="radio" id="class_xii" name="class_selection" value="XII" required>
                        <label for="class_xii">Class XII</label>
                    </div>
                </div>
                <button type="submit">Proceed</button>
            </form>
        </div>
    </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template)

@app.route('/l3_screen/<class_selection>', methods=['GET', 'POST'])
def l3_screen(class_selection):
    json_file = f'CBSE_{class_selection}.json'
    
    # Load data from selected JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)['result']['data']
    
    if request.method == 'POST':
        selected_l3 = request.form.get('l3_category')
        if selected_l3:
            return redirect(url_for('l4_l5_screen', class_selection=class_selection, l3_id=selected_l3))
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Select Category</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .container {
                width: 95%;
                margin: 0 auto;
                text-align: center;
            }
            .header {
                padding: 20px;
            }
            .form-container {
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .form-container form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .button-group {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
            .button-group div {
                margin: 5px;
            }
            .form-container button {
                margin-top: 20px;
                padding: 10px 20px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Select Category For {{data['name']}}</h1>
        </div>
        <div class="form-container">
            <form method="POST">
                <div class="button-group">
                    {% for category in data['L3'] %}
                        <div>
                            <input type="radio" id="{{ category['id'] }}" name="l3_category" value="{{ category['id'] }}" required>
                            <label for="{{ category['id'] }}">{{ category['name'] }}</label>
                        </div>
                    {% endfor %}
                </div>
                <button type="submit">Proceed</button>
            </form>
        </div>
    </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, data=data)

@app.route('/l4_l5_screen/<class_selection>/<l3_id>', methods=['GET', 'POST'])
def l4_l5_screen(class_selection, l3_id):
    json_file = f'CBSE_{class_selection}.json'
    
    # Load data from selected JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)['result']['data']
    
    l4_data = next((l3['L4'] for l3 in data['L3'] if str(l3['id']) == l3_id), [])
    
    if request.method == 'POST':
        selected_urls_by_category = {}
        
        for category in l4_data:
            selected_urls = request.form.getlist(category['name'])
            if selected_urls:
                selected_urls_by_category[category['name']] = ','.join(selected_urls)
        
        if selected_urls_by_category:
            # Serialize the dictionary to URL-encoded query string
            serialized_data = urllib.parse.urlencode(selected_urls_by_category)
            return redirect(url_for('test_page') + '?' + serialized_data)
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CBSE XI MATHS</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .container {
                width: 95%;
                margin: 0 auto;
                text-align: center;
            }
            .header {
                padding: 20px;
            }
            .form-container {
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .form-container form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .section-container {
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                width: 100%;
            }
            .button-group {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
            }
            .button-group div {
                margin: 5px;
            }
            .form-container button {
                margin-top: 20px;
                padding: 10px 20px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>CBSE XI MATHS</h1>
        </div>
        <div class="form-container">
            <form method="POST">
                {% for section in l4_data %}
                    <div class="section-container">
                        <h3>{{ section['name'] }}</h3>
                        <div class="button-group">
                            {% for test in section['L5'] %}
                                <div>
                                    <input type="checkbox" id="{{ test[10] }}" name="{{ section['name'] }}" value="{{ test[11] }}">
                                    <label for="{{ test[10] }}">{{ test[0] }}</label>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
                <button type="submit">Proceed</button>
            </form>
        </div>
    </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, l4_data=l4_data)

@app.route('/test_page', methods=['GET', 'POST'])
def test_page():
    query_params = request.query_string.decode('utf-8')
    test_urls_by_category = urllib.parse.parse_qs(query_params)
    
    # Decode the dictionary values
    for category in test_urls_by_category:
        test_urls_by_category[category] = test_urls_by_category[category][0].split(',')
    
    questions_by_section = {}
    selected_questions_ids = set()
    try:
        for category, test_urls in test_urls_by_category.items():
            questions_by_section[category] = []
            for test_url in test_urls:
                test_url = ast.literal_eval(test_url)
                json_file = test_url["file_path"]
                json_file = json_file.replace('\\', '/')
                # Load data from selected JSON file
                with open(json_file, 'r') as file:
                    data = json.load(file)['result']['data']

                
                for test_info in data:
                    if 'sec_details' in test_info:
                        for sec_detail in test_info['sec_details']:
                            for question in sec_detail.get('sec_questions', []):
                                qid = question["qid"]
                                if qid not in selected_questions_ids:
                                    selected_questions_ids.add(qid)
                                    # Determine difficulty level if not provided
                                    if 'difficulty_level' not in question:
                                        question['difficulty_level'] = determine_difficulty(json_file)
                                    else:
                                        # Ensure difficulty_level is lowercase
                                        question['difficulty_level'] = question['difficulty_level'].lower()
                                    
                                    
                                    
                                    # Clean the q_string field
                                    q_string = question['que']['1']['q_string']
                                    
                                    # Remove content inside <b> tags
                                    q_string = re.sub(r'<b>.*?</b>', '', q_string)
                                    
                                    question['que']['1']['q_string'] = q_string

                                    questions_by_section[category].append(question)
                                    # Add the question to the category
                                else:
                                    continue
                                
                    else:
                        print(f"Warning: 'sec_details' not found in test_info: {test_info}")

    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from the endpoint: {e}", 500
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}", 500
    
    if request.method == 'POST':
        selected_questions_indices = request.form.getlist('question')
        selected_questions = []
        selected_questions_ids=[]
        for idx in selected_questions_indices:
            section_name, question_index = idx.split('-')
            question_index = int(question_index)
            question = questions_by_section[section_name][question_index]
            selected_questions.append(question)

        test_name = request.form.get('test_name')
        test_time = request.form.get('test_time')
        html_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Test Details</title>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .container {
                    width: 95%;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    padding: 20px;
                }
                .test-info, .section-info, .question-list {
                    margin-bottom: 20px;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                .question-list {
                    display: flex;
                    flex-wrap: wrap;
                }
                .question {
                    width: 45%;
                    margin: 2.5%;
                }
                .question p {
                    margin: 5px 0;
                }
                .question-options ol {
                    margin-left: 20px;
                }
            </style>
        </head>
            <body>
    <div class="container">
        <div class="header">
            <h1>{{ test_name }}</h1>
            <p>Time: {{ test_time }} minutes</p>
        </div>
        <div class="question-list">
    {% for index, question in enumerate(selected_questions) %}
        <div class="question" data-qid="{{ question['qid'] }}">
            <p><strong>Question {{ index + 1 }}:</strong> {{ question['que']['1']['q_string'] | safe }}</p>
            <div class="question-options">
                <ol>
                    {% for option in question['que']['1']['q_option'] %}
                        <li>{{ option | safe }}</li>
                    {% endfor %}
                </ol>
            </div>
        </div>
    {% endfor %}
</div>
        <button onclick="submitData()">Export Selected Questions to DOCX</button>
        <button type="button" onclick="downloadSolutions('{{test_name}}')">Download Solutions</button>
    </div>

    <script>
    
        function submitData() {
            const testName = "{{ test_name }}";
            const testTime = "{{ test_time }}";
            const selectedQuestions = {{ selected_questions | tojson | safe }};

            const data = {
                test_name: testName,
                test_time: testTime,
                selected_questions: selectedQuestions
            };

            fetch('/export_to_docx', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = testName + '.docx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => console.error('Error:', error));
        }


            function downloadSolutions(testName) {
    if (!testName) {
        console.error('Test name is not provided');
        alert('Test name is missing. Please ensure you have entered a test name.');
        return;
    }

    const selectedQuestions = Array.from(document.querySelectorAll('.question'))
        .map(questionDiv => questionDiv.getAttribute('data-qid'))
        .filter(qid => qid); // Filter out any null or undefined values

    if (selectedQuestions.length === 0) {
        alert('No questions found. Please ensure questions are loaded before downloading solutions.');
        return;
    }

    const data = {
        test_name: testName,
        question_ids: selectedQuestions
    };

    fetch('/download_solutions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `${testName}_solutions.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while downloading the solutions. Please try again.');
    });
}
    </script>

        </html>
        '''
        
        return render_template_string(html_template, selected_questions=selected_questions, enumerate=enumerate, test_name=test_name, test_time=test_time)

    else:

        html_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Select Questions</title>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                .container {
                    width: 95%;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    padding: 20px;
                }
                .form-container {
                    margin: 20px 0;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                .form-container form {
                    display: flex;
                    flex-direction: column;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .form-container button {
                    margin-top: 20px;
                    padding: 10px 20px;
                    font-size: 16px;
                    align-self: center;
                }
                .collapsible {
                    background-color: #f2f2f2;
                    color: #444;
                    cursor: pointer;
                    padding: 10px;
                    width: 100%;
                    border: none;
                    text-align: left;
                    outline: none;
                    font-size: 15px;
                }
                .active, .collapsible:hover {
                    background-color: #ccc;
                }
                .content {
                    padding: 0 18px;
                    display: none;
                    overflow: hidden;
                    background-color: #f9f9f9;
                }
                .content table {
                    width: 100%;
                }
                .section-summary {
                    margin-bottom: 20px;
                }
                .summary-table {
                    width: auto;
                    margin-bottom: 10px;
                }
                .random-selection {
                    margin-bottom: 20px;
                }
                .random-input {
                    width: 50px;
                }
            </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
                <h1>Select Questions</h1>
            </div>
            <div class="form-container">
                <form method="POST">
                    {% for section, questions in questions_by_section.items() %}
                        <button type="button" class="collapsible">{{ section }}</button>
                        <div class="content">
                            <div class="section-summary">
                                <h3>Question Summary</h3>
                                <table class="summary-table">
                                    <tr>
                                        <th>Difficulty</th>
                                        <th>Total Questions</th>
                                        
                                    </tr>
                                    <tr>
                                        <td>Easy</td>
                                        <td id="{{ section }}-easy-count">0</td>
                                        
                                    </tr>
                                    <tr>
                                        <td>Moderate</td>
                                        <td id="{{ section }}-moderate-count">0</td>
                                        
                                    </tr>
                                    <tr>
                                        <td>Difficult</td>
                                        <td id="{{ section }}-difficult-count">0</td>
                                        
                                    </tr>
                                </table>
                            </div>
                            <div class="random-selection">
                                <label for="num_questions_{{ section }}">Number of Questions to Randomly Select (All Difficulties):</label>
                                <input type="number" id="num_questions_{{ section }}" name="num_questions_{{ section }}">
                                <button type="button" onclick="selectRandomQuestions('{{ section }}')">Select Random Questions</button>
                            </div>
                            <table>
                                <tr>
                                    <th><input type="checkbox" onclick="toggleSelectAll(this)"> Select All</th>
                                    <th>Question and Options</th>
                                    <th>Difficulty Level</th>
                                </tr>
                                {% for index, question in enumerate(questions) %}
                                <tr>
                                    
                                    <td><input type="checkbox" name="question" value="{{ section }}-{{ index }}" data-difficulty="{{ question['difficulty_level'] }}"></td>
                                    <td>
                                        <p><strong>Question {{ index + 1 }}:</strong> {{ question['que']['1']['q_string'] | safe }}</p>
                                        <ul>
                                            {% for option in question['que']['1']['q_option'] %}
                                                <li>{{ option | safe }}</li>
                                            {% endfor %}
                                        </ul>
                                    </td>
                                    <td>{{ question['difficulty_level'] }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    {% endfor %}
                    <label for="test_name">Test Name:</label>
                    <input type="text" id="test_name" name="test_name" required>
                    <label for="test_time">Test Time (in minutes):</label>
                    <input type="number" id="test_time" name="test_time" required>
                    <button type="submit">Create Question Paper</button>
                </form>
            </div>
        </div>
        <script>
            function toggleSelectAll(source) {
                checkboxes = source.closest('table').querySelectorAll('input[type="checkbox"]');
                for (var i = 0; i < checkboxes.length; i++) {
                    if (checkboxes[i] != source) {
                        checkboxes[i].checked = source.checked;
                    }
                }
            }
            function selectRandomQuestions(section) {
                var numQuestions = document.getElementById('num_questions_' + section).value;
                var checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"]');
                var checkboxesArray = Array.from(checkboxes);

                // Clear all checkboxes first
                checkboxesArray.forEach(function(checkbox) {
                    checkbox.checked = false;
                });

                // Shuffle array
                for (let i = checkboxesArray.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [checkboxesArray[i], checkboxesArray[j]] = [checkboxesArray[j], checkboxesArray[i]];
                }

                // Select the required number of questions
                for (let i = 0; i < numQuestions && i < checkboxesArray.length; i++) {
                    checkboxesArray[i].checked = true;
                }
            }

            function selectRandomByDifficulty(section, difficulty) {
                var numQuestions = document.getElementById(section + '-' + difficulty + '-random').value;
                var checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"][data-difficulty="' + difficulty + '"]');
                var checkboxesArray = Array.from(checkboxes);

                // Clear checkboxes of this difficulty
                checkboxesArray.forEach(function(checkbox) {
                    checkbox.checked = false;
                });

                // Shuffle array
                for (let i = checkboxesArray.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [checkboxesArray[i], checkboxesArray[j]] = [checkboxesArray[j], checkboxesArray[i]];
                }

                // Select the required number of questions
                for (let i = 0; i < numQuestions && i < checkboxesArray.length; i++) {
                    checkboxesArray[i].checked = true;
                }
            }

            function updateQuestionCounts() {
                var sections = document.getElementsByClassName('collapsible');
                for (var i = 0; i < sections.length; i++) {
                    var section = sections[i].textContent.trim();
                    var checkboxes = document.querySelectorAll('.content input[type="checkbox"][name="question"][value^="' + section + '-"]');
                    var easyCounts = 0, moderateCounts = 0, difficultCounts = 0;

                    checkboxes.forEach(function(checkbox) {
                        switch(checkbox.getAttribute('data-difficulty').toLowerCase()) {
                            case 'easy':
                                easyCounts++;
                                break;
                            case 'moderate':
                                moderateCounts++;
                                break;
                            case 'difficult':
                                difficultCounts++;
                                break;
                        }
                    });

                    document.getElementById(section + '-easy-count').textContent = easyCounts;
                    document.getElementById(section + '-moderate-count').textContent = moderateCounts;
                    document.getElementById(section + '-difficult-count').textContent = difficultCounts;
                }
            }

            var coll = document.getElementsByClassName("collapsible");
            var i;

            for (i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                        updateQuestionCounts(); // Update counts when section is opened
                    }
                });
            }

            // Call updateQuestionCounts when the page loads
            window.onload = updateQuestionCounts;
        </script>
        </body>
        </html>
        '''
        
        return render_template_string(html_template, questions_by_section=questions_by_section, enumerate=enumerate)

@app.route('/download_solutions', methods=['POST'])
def download_solutions():
    data = request.json
    test_name = data['test_name']
    question_ids = data['question_ids']
    
    # Load the solutions from the JSON file with UTF-8 encoding
    with open('Answers/solutions.json', 'r', encoding='utf-8') as f:
        solutions = json.load(f)
    
    # Create a DOCX document
    doc = Document()
    doc.add_heading(f'Solutions for {test_name}', level=1)
    
    # Add solutions to the document
    for index, qid in enumerate(question_ids, start=1):
        correct_answers = solutions.get(qid, {}).get('correct_answers', 'solution not found')
        solution = solutions.get(str(correct_answers), 'Solution not found')
        doc.add_heading(f'Question {index}', level=2)
        doc.add_paragraph(solution)
    
    # Save the document
    docx_filename = f'{test_name}_solutions.docx'
    doc.save(docx_filename)
    
    return send_file(docx_filename, as_attachment=True, download_name=f'{test_name}_solutions.docx')

def determine_difficulty(question):
    # Example logic to determine difficulty
    # This should be replaced with actual logic based on your criteria
    if 'easy' in question.lower():
        return 'Easy'
    elif 'moderate' in question.lower():
        return 'Moderate'
    else:
        return 'Difficult'


@app.route('/export_to_docx', methods=['POST'])
def export_to_docx():
    try:
        data = request.get_json(force=True)  # force=True to handle potential mismatched content type
        
        # Pre-process JSON to escape backslashes
        data_str = json.dumps(data)
        # data_str = data_str.replace('\\', '\\\\')
        data = json.loads(data_str)
        
        test_name = data['test_name']
        selected_questions = data['selected_questions']
        
        output_docx_file = 'output.docx'
        convert_json_to_docx(selected_questions, output_docx_file, test_name)

        return send_file(output_docx_file, as_attachment=True, download_name=f'{test_name}.docx')
    except Exception as e:
        print(f"Error in export_to_docx: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Utility Functions

def clean_html(raw_html):
    clean = re.sub(r'<style>.*?</style>', '', raw_html, flags=re.DOTALL)
    clean = clean.replace('<br/>', '\n')
    clean = re.sub(r'<[^>]+>', '', clean)
    return clean.strip()

def process_latex(text):
    text = re.sub(r'\\mathrm{([^}]+)}', r'\\mathrm{\1}', text)
    text = re.sub(r'\\\(|\\\)', '$', text)
    text = re.sub(r'(\$[^$]+)\$\s*(\$[^$]+\$)', r'\1\2', text)
    return text

def latex_to_markdown(latex):
    latex = re.sub(r'<fmath.*?>(.*?)</fmath>', r'$\1$', latex)
    latex = process_latex(latex)
    latex = re.sub(r'\\([a-zA-Z]+)', r'\\\1', latex)
    latex = re.sub(r'\s+', ' ', latex)
    return latex

def handle_images(content):
    img_pattern = r'<img[^>]+src="([^">]+)"[^>]*>'
    return re.sub(img_pattern, r'![Image](\1)', content)

def handle_tables(content):
    tables = re.findall(r'<table.*?</table>', content, re.DOTALL)
    for table in tables:
        soup = BeautifulSoup(table, 'html.parser')
        markdown_table = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            markdown_row = '| ' + ' | '.join([col.get_text(strip=True) for col in cols]) + ' |'
            markdown_table.append(markdown_row)
        markdown_table = '\n'.join(markdown_table)
        content = content.replace(table, markdown_table)
    return content

def json_to_markdown(json_data, test_name):
    questions = json.loads(json_data)
    markdown_content = f"# {test_name}\n\n"
    
    for index, question in enumerate(questions, 1):
        markdown_content += f"## Question {index}\n\n"
        q_string = question['que']['1']['q_string']
        
        q_string = handle_images(q_string)
        q_string = handle_tables(q_string)
        q_string = latex_to_markdown(q_string)
        q_string = clean_html(q_string)
        
        markdown_content += f"{q_string}\n\n"
        
        if 'q_option' in question['que']['1']:
            for i, option in enumerate(question['que']['1']['q_option'], 65):
                option_text = option
                option_text = handle_images(option_text)
                option_text = handle_tables(option_text)
                option_text = latex_to_markdown(option_text)
                option_text = clean_html(option_text)
                markdown_content += f"{chr(i)}) {option_text}\n"
            markdown_content += "\n"
        
        # markdown_content += f"Max Marks: {question.get('max_marks', 'N/A')}, Negative Marks: {question.get('neg_marks', 'N/A')}\n\n"
    
    return markdown_content

def set_two_columns(docx_file):
    document = Document(docx_file)
    for section in document.sections:
        sectPr = section._sectPr
        cols = OxmlElement('w:cols')
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '720')
        sectPr.append(cols)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
    document.save(docx_file)
    print(f"DOCX file '{docx_file}' has been updated to two columns.")

def convert_json_to_docx(selected_questions, docx_file, test_name):
    try:
        json_data = json.dumps(selected_questions)
        markdown_output = json_to_markdown(json_data, test_name)

        # Print Markdown content to console
        print(markdown_output)
        
        # Convert Markdown to DOCX using pypandoc
        pypandoc.convert_text(markdown_output, 'docx', format='md', outputfile=docx_file)
        
        # Adjust DOCX to two columns
        set_two_columns(docx_file)

        print(f"\nDOCX file '{docx_file}' has been created and updated to two columns successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{selected_questions}' was not found.")
    except json.JSONDecodeError:
        print("Error: The JSON data is not properly formatted.")
    except KeyError as e:
        print(f"Error: The key {e} was not found in the JSON data.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


webview.create_window('KodeMapa-Exampad', app)
if __name__ == "__main__":
    app.run(debug=True)
    # webview.start()