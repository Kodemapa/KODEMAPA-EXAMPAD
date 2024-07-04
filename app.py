import ast
import random
import re
from flask import Flask, jsonify, render_template_string, request, redirect, url_for , send_file,render_template
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

    # document = Document()
    # with open(pdf_filename, 'rb') as pdf_file:
    #     pdf_content = pdf_file.read()
    # document.add_paragraph(pdf_content.decode('utf-8'))
    # document.save(docx_filename)

# @app.route('/export_to_docx', methods=['POST'])
# def export_to_docx():
#     try:
#         data = request.get_json()
#         test_name = data['test_name']
#         selected_questions = data['selected_questions']
#         template_filename = test_name + '.tex'
#         docx_filename = test_name + '.docx'

#         latex_content = generate_latex_content(selected_questions, test_name)

#         print("Generated LaTeX content:")
#         print(latex_content)

#         with open(template_filename, 'w', encoding='utf-8') as f:
#             f.write(latex_content)

#         convert_latex_to_docx(template_filename, docx_filename)
#         return send_file(docx_filename, as_attachment=True, download_name=test_name + '.docx')
#     except Exception as e:
#         print(f"Error in export_to_docx: {str(e)}")
#         return jsonify({"error": str(e)}), 500
   

# def html_table_to_latex(html_table):
#     # Remove any attributes from the tags
#     html_table = re.sub(r'<(\w+)[^>]*>', r'<\1>', html_table)
    
#     # Find all rows
#     rows = re.findall(r'<tr>(.*?)</tr>', html_table, re.DOTALL)
#     if not rows:
#         return "% Error: No table rows found"

#     # Determine the number of columns
#     first_row = re.findall(r'<t[dh]>(.*?)</t[dh]>', rows[0], re.DOTALL)
#     num_cols = len(first_row)
    
#     if num_cols == 0:
#         return "% Error: No table cells found"

#     # Start the LaTeX table
#     latex_table = '\\begin{tabular}{|' + 'c|' * num_cols + '}\n\\hline\n'

#     for row in rows:
#         cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
#         cells += [''] * (num_cols - len(cells))  # Pad if necessary
#         latex_table += ' & '.join(cells) + ' \\\\\n\\hline\n'

#     latex_table += '\\end{tabular}'
#     return latex_table


# def convert_math(text):
#     # Convert inline math
#     text = re.sub(r'\$(.+?)\$', r'$\1$', text)
    
#     # Convert specific mathematical symbols and expressions
#     math_replacements = [
#         ('in', r'\in'),
#         ('leq', r'\leq'),
#         ('geq', r'\geq'),
#         ('subset', r'\subset'),
#         ('cup', r'\cup'),
#         ('cap', r'\cap'),
#         ('emptyset', r'\emptyset'),
#         (r'left\(', r'\left('),
#         (r'right\)', r'\right)'),
#         (r'left\{', r'\left\{'),
#         (r'right\}', r'\right\}'),
#         (r'left\|', r'\left|'),
#         (r'right\|', r'\right|'),
#         (r'(\d+)\^(\w+)', r'$\1^{\2}$'),  # Handle superscripts
#         (r'\\{', r'\{'),
#         (r'\\}', r'\}'),
#         ('PAc', r'P(A^c)'),
#         ('PB', r'P(B)'),
#         ('PA ∩ Bc', r'P(A \cap B^c)'),
#         ('PBA ∩ Bc', r'P(B|A \cap B^c)'),
#         ('P(Ac)', r'P(A^c)'),
#         ('P(Bc)', r'P(B^c)'),
#         ('P(A ∩ Bc)', r'P(A \cap B^c)'),
#         ('P[(B)/(A∩Bc)]', r'P\left[\frac{B}{A \cap B^c}\right]'),
#         ('∩', r'\cap'),
#         ('∪', r'\cup'),
#         ('≤', r'\leq'),
#         ('≥', r'\geq'),
#     ]
    
#     for old, new in math_replacements:
#         text = re.sub(r'\b' + old + r'\b', new, text)
    
#     # Handle more complex expressions
#     text = re.sub(r'\((.+?)\)', lambda m: r'$(' + m.group(1) + r')$', text)
    
#     # Convert fractions
#     text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
    
#     return text

# def html_to_latex(html):
#     try:
#         html = unescape(html)
        
#         # Handle tables
#         html = re.sub(r'<table.*?>(.*?)</table>', lambda m: html_table_to_latex(m.group(0)), html, flags=re.DOTALL)
        
#         # Handle math content
#         html = re.sub(r'<span class="mathMlContainer".*?>(.*?)</span>', lambda m: '$' + m.group(1) + '$', html, flags=re.DOTALL)
        
#         # Handle paragraphs
#         html = re.sub(r'<p.*?>(.*?)</p>', r'\n\1\n', html, flags=re.DOTALL)
        
#         # Handle line breaks
#         html = re.sub(r'<br.*?>', r'\\\\', html)
        
#         # Remove other HTML tags
#         html = re.sub(r'<.*?>', '', html)
        
#         # Convert mathematical content
#         html = convert_math(html)
        
#         return html.strip()
    
#     except Exception as e:
#         print(f"Error in html_to_latex: {str(e)}")
#         return html



# def generate_latex_content(selected_questions, test_name):
#     latex_content = r'''\documentclass{article}
# \usepackage{amsmath}
# \usepackage{amssymb}
# \usepackage{graphicx}
# \usepackage{enumitem}
# \usepackage{longtable}
# \usepackage{geometry}
# \geometry{margin=1in}
# \title{%s}
# \begin{document}
# \maketitle
# ''' % test_name

#     for index, question in enumerate(selected_questions, start=1):
#         q_string = html_to_latex(question['que']['1']['q_string'])
#         q_options = [html_to_latex(opt) for opt in question['que']['1']['q_option']]

#         latex_content += r'\section*{Question %d}' % index + '\n'
#         latex_content += q_string + '\n\n'
#         latex_content += r'\begin{enumerate}[label=(\alph*)]' + '\n'
#         for option in q_options:
#             latex_content += r'\item $' + option + '$\n'
#         latex_content += r'\end{enumerate}' + '\n\n'
        
#         if index < len(selected_questions):
#             latex_content += r'\newpage' + '\n'

#     latex_content += r'\end{document}'
#     return latex_content

# def escape_latex(text):
#     special_chars = ['\\', '_', '%', '&', '#', '$', '{', '}', '^', '~']
#     for char in special_chars:
#         text = text.replace(char, '\\' + char)
#     return text

# def cleanup_latex(content):
#     # Remove any trailing \newpage commands
#     content = re.sub(r'\n*\\newpage\s*$', '', content)
    
#     # Ensure all environments are closed
#     open_envs = re.findall(r'\\begin\{(\w+)\}', content)
#     for env in reversed(open_envs):
#         if f'\\end{{{env}}}' not in content:
#             content += f'\n\\end{{{env}}}'
    
#     return content


# def convert_latex_to_docx(latex_filename, docx_filename):
#     try:
#         print(f"Converting {latex_filename} to {docx_filename}")
#         result = subprocess.run(['pandoc', latex_filename, '-o', docx_filename], 
#                                 capture_output=True, text=True, check=True)
#         print("Conversion successful")
#         print("Pandoc output:", result.stdout)
#     except subprocess.CalledProcessError as e:
#         print(f"Error in convert_latex_to_docx: {e}")
#         print("Pandoc error output:", e.stderr)
#         raise


from flask import Flask, request, send_file, jsonify
import subprocess
import re
from html import unescape
from pylatexenc.latexencode import unicode_to_latex
from html2text import html2text
from sympy import latex as sympy_latex
from sympy.parsing.latex import parse_latex

@app.route('/export_to_docx', methods=['POST'])
def export_to_docx():
    try:
        data = request.get_json()
        test_name = data['test_name']
        selected_questions = data['selected_questions']
        template_filename = test_name + '.tex'
        docx_filename = test_name + '.docx'

        latex_content = generate_latex_content(selected_questions, test_name)

        print("Generated LaTeX content:")
        print(latex_content)

        with open(template_filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        convert_latex_to_docx(template_filename, docx_filename)
        return send_file(docx_filename, as_attachment=True, download_name=test_name + '.docx')
    except Exception as e:
        print(f"Error in export_to_docx: {str(e)}")
        return jsonify({"error": str(e)}), 500

def html_table_to_latex(html_table):
    html_table = re.sub(r'<(\w+)[^>]*>', r'<\1>', html_table)
    rows = re.findall(r'<tr>(.*?)</tr>', html_table, re.DOTALL)
    if not rows:
        return "% Error: No table rows found"

    first_row = re.findall(r'<t[dh]>(.*?)</t[dh]>', rows[0], re.DOTALL)
    num_cols = len(first_row)
    if num_cols == 0:
        return "% Error: No table cells found"

    latex_table = '\\begin{tabular}{|' + 'c|' * num_cols + '}\n\\hline\n'

    for row in rows:
        cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
        cells += [''] * (num_cols - len(cells))
        latex_table += ' & '.join(cells) + ' \\\\\n\\hline\n'

    latex_table += '\\end{tabular}'
    return latex_table

def convert_math(text):
    text = re.sub(r'\$(.+?)\$', r'$\1$', text)
    math_replacements = [
        ('in', r'\in'),
        ('leq', r'\leq'),
        ('geq', r'\geq'),
        ('subset', r'\subset'),
        ('cup', r'\cup'),
        ('cap', r'\cap'),
        ('emptyset', r'\emptyset'),
        (r'left\(', r'\left('),
        (r'right\)', r'\right)'),
        (r'left\{', r'\left\{'),
        (r'right\}', r'\right\}'),
        (r'left\|', r'\left|'),
        (r'right\|', r'\right|'),
        (r'(\d+)\^(\w+)', r'$\1^{\2}$'),
        (r'\\{', r'\{'),
        (r'\\}', r'\}'),
        ('PAc', r'P(A^c)'),
        ('PB', r'P(B)'),
        ('PA ∩ Bc', r'P(A \cap B^c)'),
        ('PBA ∩ Bc', r'P(B|A \cap B^c)'),
        ('P(Ac)', r'P(A^c)'),
        ('P(Bc)', r'P(B^c)'),
        ('P(A ∩ Bc)', r'P(A \cap B^c)'),
        ('P[(B)/(A∩Bc)]', r'P\left[\frac{B}{A \cap B^c}\right]'),
        ('∩', r'\cap'),
        ('∪', r'\cup'),
        ('≤', r'\leq'),
        ('≥', r'\geq'),
    ]
    for old, new in math_replacements:
        text = re.sub(r'\b' + old + r'\b', new, text)
    text = re.sub(r'\((.+?)\)', lambda m: r'$(' + m.group(1) + r')$', text)
    text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
    return text

def html_to_latex(html):
    try:
        html = unescape(html)
        html = html2text(html)
        html = unicode_to_latex(html)
        
        # Handle images
        html = re.sub(r'<img\s+.*?src="(.*?)".*?>', r'\\includegraphics[width=\\linewidth]{\1}', html, flags=re.DOTALL)
        
        # Handle tables
        html = re.sub(r'<table.*?>(.*?)</table>', lambda m: html_table_to_latex(m.group(0)), html, flags=re.DOTALL)
        
        # Convert mathematical expressions
        html = re.sub(r'\$(.*?)\$', lambda m: sympy_latex(parse_latex(m.group(1))), html)
        
        return html.strip()
    
    except Exception as e:
        print(f"Error in html_to_latex: {str(e)}")
        return html

def generate_latex_content(selected_questions, test_name):
    latex_content = r'''\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{longtable}
\usepackage{geometry}
\geometry{margin=1in}
\title{%s}
\begin{document}
\maketitle
''' % test_name

    for index, question in enumerate(selected_questions, start=1):
        q_string = html_to_latex(question['que']['1']['q_string'])
        q_options = [html_to_latex(opt) for opt in question['que']['1']['q_option']]

        latex_content += r'\section*{Question %d}' % index + '\n'
        latex_content += q_string + '\n\n'
        latex_content += r'\begin{enumerate}[label=(\alph*)]' + '\n'
        for option in q_options:
            latex_content += r'\item ' + option + '\n'
        latex_content += r'\end{enumerate}' + '\n\n'
        
        if index < len(selected_questions):
            latex_content += r'\newpage' + '\n'

    latex_content += r'\end{document}'
    return latex_content

def convert_latex_to_docx(latex_filename, docx_filename):
    try:
        print(f"Converting {latex_filename} to {docx_filename}")
        result = subprocess.run(['pandoc', latex_filename, '-o', docx_filename], 
                                capture_output=True, text=True, check=True)
        print("Conversion successful")
        print("Pandoc output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error in convert_latex_to_docx: {e}")
        print("Pandoc error output:", e.stderr)
        raise

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



    # def convert_math(text):
#     # Convert inline math
#     text = re.sub(r'\$(.+?)\$', r'$\1$', text)
    
#     # Convert specific mathematical symbols and expressions
#     math_replacements = [
#         ('in', r'\in'),
#         ('leq', r'\leq'),
#         ('geq', r'\geq'),
#         ('subset', r'\subset'),
#         ('cup', r'\cup'),
#         ('cap', r'\cap'),
#         ('emptyset', r'\emptyset'),
#         (r'left\(', r'\left('),
#         (r'right\)', r'\right)'),
#         (r'left\{', r'\left\{'),
#         (r'right\}', r'\right\}'),
#         (r'left\|', r'\left|'),
#         (r'right\|', r'\right|'),
#         (r'(\d+)\^(\w+)', r'$\1^{\2}$'),  # Handle superscripts
#         (r'\\{', r'\{'),
#         (r'\\}', r'\}'),
#     ]
    
#     for old, new in math_replacements:
#         text = re.sub(r'\b' + old + r'\b', new, text)
    
#     # Handle more complex expressions
#     text = re.sub(r'\((.+?)\)', lambda m: r'$(' + m.group(1) + r')$', text)
    
#     return text

# def html_to_latex(html):
#     try:
#         html = unescape(html)
        
#         # Handle tables
#         html = re.sub(r'<table.*?>(.*?)</table>', lambda m: html_table_to_latex(m.group(0)), html, flags=re.DOTALL)
        
#         # Handle math content
#         html = re.sub(r'<span class="mathMlContainer".*?>(.*?)</span>', lambda m: '$' + m.group(1) + '$', html, flags=re.DOTALL)
        
#         # Handle paragraphs
#         html = re.sub(r'<p.*?>(.*?)</p>', r'\n\1\n', html, flags=re.DOTALL)
        
#         # Handle line breaks
#         html = re.sub(r'<br.*?>', r'\\\\', html)
        
#         # Remove other HTML tags
#         html = re.sub(r'<.*?>', '', html)
        
#         # Convert mathematical content
#         html = convert_math(html)
        
#         return html.strip()
    
#     except Exception as e:
#         print(f"Error in html_to_latex: {str(e)}")
#         return html

# def generate_latex_content(selected_questions, test_name):
#     latex_content = r'''\documentclass{article}
# \usepackage{amsmath}
# \usepackage{amssymb}
# \usepackage{graphicx}
# \usepackage{enumitem}
# \usepackage{longtable}
# \usepackage{geometry}
# \geometry{margin=1in}
# \title{%s}
# \begin{document}
# \maketitle
# ''' % test_name

#     for index, question in enumerate(selected_questions, start=1):
#         q_string = html_to_latex(question['que']['1']['q_string'])
#         q_options = [html_to_latex(opt) for opt in question['que']['1']['q_option']]

#         latex_content += r'\section*{Question %d}' % index + '\n'
#         latex_content += q_string + '\n\n'
#         latex_content += r'\begin{enumerate}[label=(\alph*)]' + '\n'
#         for option in q_options:
#             latex_content += r'\item ' + option + '\n'
#         latex_content += r'\end{enumerate}' + '\n\n'
        
#         if index < len(selected_questions):
#             latex_content += r'\newpage' + '\n'

#     latex_content += r'\end{document}'
#     return latex_content


# def html_table_to_latex(html_table):
#     # Remove any attributes from the tags
#     html_table = re.sub(r'<(\w+)[^>]*>', r'<\1>', html_table)
    
#     # Find all rows
#     rows = re.findall(r'<tr>(.*?)</tr>', html_table, re.DOTALL)
#     if not rows:
#         return "% Error: No table rows found"

#     # Determine the number of columns
#     first_row = re.findall(r'<t[dh]>(.*?)</t[dh]>', rows[0], re.DOTALL)
#     num_cols = len(first_row)
    
#     if num_cols == 0:
#         return "% Error: No table cells found"

#     # Start the LaTeX table
#     latex_table = '\\begin{tabular}{|' + 'c|' * num_cols + '}\n\\hline\n'

#     for row in rows:
#         cells = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
#         cells += [''] * (num_cols - len(cells))  # Pad if necessary
#         cells = [convert_math(cell) for cell in cells]  # Convert math in cells
#         latex_table += ' & '.join(cells) + ' \\\\\n\\hline\n'

#     latex_table += '\\end{tabular}'
#     return latex_table
