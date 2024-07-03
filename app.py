import ast
import random
import re
from flask import Flask, jsonify, render_template_string, request, redirect, url_for , send_file,render_template
import json
import pypandoc
pypandoc.download_pandoc()
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
    
    return render_template('select_class.html')

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
    
    return render_template('select_category.html', data=data)

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
    
    return render_template('cbse_xi_maths.html', l4_data=l4_data)

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
        return render_template('test_details.html', selected_questions=selected_questions, enumerate=enumerate, test_name=test_name, test_time=test_time)

    else:

        return render_template('select_questions.html', questions_by_section=questions_by_section, enumerate=enumerate)

def compile_latex_to_pdf(template_filename):
    # Compile LaTeX to PDF
    subprocess.run(['pdflatex', '-interaction=nonstopmode', template_filename])

def convert_pdf_to_docx(pdf_filename, docx_filename):
    # Convert PDF to DOCX using python-docx library
    cv = Converter(pdf_filename)
    cv.convert(docx_filename, start=0, end=None)
    cv.close()


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