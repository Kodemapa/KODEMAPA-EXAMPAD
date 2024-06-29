import ast
import random
import re
from flask import Flask, jsonify, render_template_string, request, redirect, url_for , send_file
import json
import pypandoc
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
                <div class="question">
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

def compile_latex_to_pdf(template_filename):
    # Compile LaTeX to PDF
    subprocess.run(['pdflatex', '-interaction=nonstopmode', template_filename])

def convert_pdf_to_docx(pdf_filename, docx_filename):
    # Convert PDF to DOCX using python-docx library
    cv = Converter(pdf_filename)
    cv.convert(docx_filename, start=0, end=None)
    cv.close()

    # document = Document()
    # with open(pdf_filename, 'rb') as pdf_file:
    #     pdf_content = pdf_file.read()
    # document.add_paragraph(pdf_content.decode('utf-8'))
    # document.save(docx_filename)

@app.route('/export_to_docx', methods=['Post'])
def export_to_docx():
    # template_filename = 'template.tex'
    # pdf_filename = 'output.pdf'
    # test_name = request.form.get('test_name')
    data = request.get_json()
    test_name = data['test_name']
    selected_questions = data['selected_questions']
    template_filename = test_name+'.tex'
    pdf_filename = 'output.pdf'
    docx_filename = test_name + '.docx'

    # selected_questions = request.form.getlist('selected_questions')
    # test_name = request.form.get('test_name')
    # Generate LaTeX content from selected_questions
    latex_content = generate_latex_content(selected_questions,test_name)

    # Write LaTeX content to template.tex
    with open(template_filename, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    # # Compile LaTeX to PDF
    # compile_latex_to_pdf(template_filename)

    # # # Convert PDF to DOCX
    # convert_pdf_to_docx(pdf_filename, docx_filename)
    convert_latex_to_docx(template_filename, docx_filename)
    return send_file(docx_filename, as_attachment=True, download_name=test_name + '.docx')


def html_table_to_latex(html):
    """Convert HTML table to LaTeX tabular environment."""
    html = unescape(html)

    # Remove any attributes from the tags
    html = re.sub(r'<table[^>]*>', '<table>', html)
    html = re.sub(r'<tr[^>]*>', '<tr>', html)
    html = re.sub(r'<td[^>]*>', '<td>', html)
    html = re.sub(r'<th[^>]*>', '<th>', html)

    # Initialize LaTeX table
    latex_table = '\\begin{tabular}{|' + 'c|' * html.count('<tr>') + '}\n\\hline\n'

    # Process table rows and cells
    html = html.replace('<table>', '')
    html = html.replace('</table>', '')
    html = html.replace('<tbody>', '')
    html = html.replace('</tbody>', '')
    rows = html.split('</tr>')

    for row in rows:
        if '<tr>' in row:
            row = row.replace('<tr>', '')
            cells = row.split('</td>')
            for cell in cells:
                if '<td>' in cell:
                    cell = cell.replace('<td>', '').strip()
                    latex_table += cell + ' & '
                elif '<th>' in cell:
                    cell = cell.replace('<th>', '').strip()
                    latex_table += '\\textbf{' + cell + '} & '
            latex_table = latex_table.rstrip(' & ')
            latex_table += ' \\\\\n\\hline\n'

    latex_table += '\\end{tabular}\n'
    return latex_table

def html_to_latex(html):
    """Converts HTML content to LaTeX."""
    # Unescape HTML entities
    html = unescape(html)

    # Replace HTML tags with LaTeX equivalents
    replacements = [
        (r"<p>", r""),
        (r"</p>", r""),
        (r"<sup>", r"$^{"),
        (r"</sup>", r"}$"),
        (r"<sub>", r"$_{"),
        (r"</sub>", r"}$"),
        (r"<b>", r"\\textbf{"),
        (r"</b>", r"}"),
        (r"<i>", r"\\textit{"),
        (r"</i>", r"}"),
        (r"&nbsp;", r"~"),
        (r"&gt;", r">"),
        (r"&lt;", r"<"),
        (r"&amp;", r"&"),
        (r'<br\s*/?>', r"\\newline"),
        (r'<span[^>]*>', r""),
        (r'</span>', r""),
        (r'<div[^>]*>', r""),
        (r'</div>', r"")
    ]
    for old, new in replacements:
        html = re.sub(old, new, html, flags=re.IGNORECASE)

    # Convert <img> tags to LaTeX \includegraphics
    img_tags = re.findall(r'<img[^>]+>', html, flags=re.IGNORECASE)
    for img_tag in img_tags:
        src_match = re.search(r'src="([^"]+)"', img_tag)
        if src_match:
            src = src_match.group(1)
            latex_img = r'\includegraphics[width=\textwidth]{%s}' % src
            html = html.replace(img_tag, latex_img)

    # Convert <table> tags to LaTeX tabular environment
    html = re.sub(r'<table[^>]*>.*?</table>', lambda x: html_table_to_latex(x.group()), html, flags=re.DOTALL)

    return html

# def generate_latex_content(selected_questions, test_name):
#     # Start the LaTeX document
#     latex_content = r'''\documentclass{article}
#                     \usepackage{amsmath}
#                     \usepackage{amssymb}
#                     \usepackage{graphicx}
#                     \usepackage{enumitem}
#                     \usepackage{longtable}
#                     \title{%s}
#                     \begin{document}
#                     \maketitle
#                     ''' % test_name

#     # Generate LaTeX content from selected_questions
#     for index, question in enumerate(selected_questions, start=1):
#         q_string = html_to_latex(question['que']['1']['q_string'])
#         q_options = [html_to_latex(opt) for opt in question['que']['1']['q_option']]

#         latex_content += r'\section*{Question %d}' % index + '\n'
#         latex_content += q_string + '\n'
#         latex_content += r'\begin{enumerate}[label=(\alph*)]' + '\n'
#         for option in q_options:
#             latex_content += r'\item ' + option + '\n'
#         latex_content += r'\end{enumerate}' + '\n'
#         latex_content += r'\newpage' + '\n'

#     # End the LaTeX document
#     latex_content += r'\end{document}'
#     return latex_content

# def convert_latex_to_docx(latex_filename, docx_filename):
#     # Convert LaTeX to DOCX using pypandoc
#     pypandoc.convert_file(latex_filename, 'docx', outputfile=docx_filename)

# import time 
# @app.route('/export_to_docx', methods=['POST'])
# def export_to_docx(selected_questions, test_name):
#     # Generate LaTeX content from selected_questions
#     latex_content = generate_latex_content(selected_questions, test_name)

#     temp_dir = tempfile.mkdtemp()

#     try:
#         # Convert LaTeX content directly to DOCX in a temporary file
#         temp_latex_filename = os.path.join(temp_dir, test_name + '.tex')
#         with open(temp_latex_filename, 'w', encoding='utf-8') as temp_latex_file:
#             temp_latex_file.write(latex_content)

#         temp_docx_filename = os.path.join(temp_dir, test_name + '.docx')

#         # Convert LaTeX to DOCX using pypandoc
#         convert_latex_to_docx(temp_latex_filename, temp_docx_filename)

#         # Check if the DOCX file was created successfully
#         if os.path.exists(temp_docx_filename):
#             # Send the file as a download
#             return send_file(temp_docx_filename, as_attachment=True, download_name=test_name + '.docx')
#         else:
#             # Handle case where the file was not created
#             return jsonify({'error': 'Failed to generate DOCX file'}), 500

#     finally:
#         # Clean up temporary files
#         if os.path.exists(temp_latex_filename):
#             os.remove(temp_latex_filename)
#         if os.path.exists(temp_docx_filename):
#             try:
#                 os.remove(temp_docx_filename)
#             except PermissionError:
#                 # Handle PermissionError if the file is still in use
#                 pass

#         # Clean up the temporary directory
#         try:
#             os.rmdir(temp_dir)
#         except OSError as e:
#             print(f"Error removing temporary directory {temp_dir}: {e}")

# def html_table_to_latex(html):
#     """Convert HTML table to LaTeX tabular environment."""
#     html = unescape(html)

#     # Remove any attributes from the tags
#     html = re.sub(r'<table[^>]*>', '<table>', html)
#     html = re.sub(r'<tr[^>]*>', '<tr>', html)
#     html = re.sub(r'<td[^>]*>', '<td>', html)
#     html = re.sub(r'<th[^>]*>', '<th>', html)

#     # Initialize LaTeX table
#     latex_table = '\\begin{tabular}{|' + 'c|' * html.count('<tr>') + '}\n\\hline\n'

#     # Process table rows and cells
#     html = html.replace('<table>', '')
#     html = html.replace('</table>', '')
#     html = html.replace('<tbody>', '')
#     html = html.replace('</tbody>', '')
#     rows = html.split('</tr>')

#     for row in rows:
#         if '<tr>' in row:
#             row = row.replace('<tr>', '')
#             cells = row.split('</td>')
#             for cell in cells:
#                 if '<td>' in cell:
#                     cell = cell.replace('<td>', '').strip()
#                     latex_table += cell + ' & '
#                 elif '<th>' in cell:
#                     cell = cell.replace('<th>', '').strip()
#                     latex_table += '\\textbf{' + cell + '} & '
#             latex_table = latex_table.rstrip(' & ')
#             latex_table += ' \\\\\n\\hline\n'

#     latex_table += '\\end{tabular}\n'
#     return latex_table

def html_to_latex(html):
    """Converts HTML content to LaTeX."""
    # Unescape HTML entities
    html = unescape(html)

    # Replace HTML tags with LaTeX equivalents
    replacements = [
        (r"<p>", r""),
        (r"</p>", r""),
        (r"<sup>", r"$^{"),
        (r"</sup>", r"}$"),
        (r"<sub>", r"$_{"),
        (r"</sub>", r"}$"),
        (r"<b>", r"\\textbf{"),
        (r"</b>", r"}"),
        (r"<i>", r"\\textit{"),
        (r"</i>", r"}"),
        (r"&nbsp;", r"~"),
        (r"&gt;", r">"),
        (r"&lt;", r"<"),
        (r"&amp;", r"&"),
        (r'<br\s*/?>', r"\\newline"),
        (r'<span[^>]*>', r""),
        (r'</span>', r""),
        (r'<div[^>]*>', r""),
        (r'</div>', r"")
    ]
    for old, new in replacements:
        html = re.sub(old, new, html, flags=re.IGNORECASE)

    # Convert <img> tags to LaTeX \includegraphics
    img_tags = re.findall(r'<img[^>]+>', html, flags=re.IGNORECASE)
    for img_tag in img_tags:
        src_match = re.search(r'src="([^"]+)"', img_tag)
        if src_match:
            src = src_match.group(1)
            latex_img = r'\includegraphics[width=\textwidth]{%s}' % src
            html = html.replace(img_tag, latex_img)

    # Convert <table> tags to LaTeX tabular environment
    html = re.sub(r'<table[^>]*>.*?</table>', lambda x: html_table_to_latex(x.group()), html, flags=re.DOTALL)

    return html

def generate_latex_content(selected_questions, test_name):
    # Start the LaTeX document
    latex_content = r'''\documentclass{article}
                    \usepackage{amsmath}
                    \usepackage{amssymb}
                    \usepackage{graphicx}
                    \usepackage{enumitem}
                    \usepackage{longtable}
                    \title{%s}
                    \begin{document}
                    \maketitle
                    ''' % test_name

    # Generate LaTeX content from selected_questions
    for index, question in enumerate(selected_questions, start=1):
        q_string = html_to_latex(question['que']['1']['q_string'])
        q_options = [html_to_latex(opt) for opt in question['que']['1']['q_option']]

        latex_content += r'\section*{Question %d}' % index + '\n'
        latex_content += q_string + '\n'
        latex_content += r'\begin{enumerate}[label=(\alph*)]' + '\n'
        for option in q_options:
            latex_content += r'\item ' + option + '\n'
        latex_content += r'\end{enumerate}' + '\n'
        latex_content += r'\newpage' + '\n'

    # End the LaTeX document
    latex_content += r'\end{document}'
    return latex_content

def convert_latex_to_docx(latex_filename, docx_filename):
    # Convert LaTeX to DOCX using pypandoc
    pypandoc.convert_file(latex_filename, 'docx', outputfile=docx_filename)


def determine_difficulty(question):
    # Example logic to determine difficulty
    # This should be replaced with actual logic based on your criteria
    if 'easy' in question.lower():
        return 'Easy'
    elif 'moderate' in question.lower():
        return 'Moderate'
    else:
        return 'Difficult'


webview.create_window('KodeMapa-Exampad', app)
if __name__ == "__main__":
    app.run(debug=True)
    # webview.start()