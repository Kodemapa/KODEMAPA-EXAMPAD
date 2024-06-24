from flask import Flask, render_template_string, request, redirect, url_for
import json
import requests
import urllib.parse

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def l3_screen():
    # Load data from local JSON file
    with open('CBSE_XI.json', 'r') as file:
        data = json.load(file)['result']['data']
    
    if request.method == 'POST':
        selected_l3 = request.form.get('l3_category')
        if selected_l3:
            return redirect(url_for('l4_l5_screen', l3_id=selected_l3))
    
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

@app.route('/l4_l5_screen/<l3_id>', methods=['GET', 'POST'])
def l4_l5_screen(l3_id):
    # Load data from local JSON file
    with open('CBSE_XI.json', 'r') as file:
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
                                    <input type="checkbox" id="{{ test[5] }}" name="{{ section['name'] }}" value="{{ test[5] }}">
                                    <label for="{{ test[5] }}">{{ test[0] }}</label>
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

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8,fi;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',  # Ensure Content-Type is application/json
         'Cookie': 'G_ENABLED_IDPS=google; __stripe_mid=5348a0e2-0460-4150-b6c5-96020a471031008362; client_meta=%7B%22homepage_masthead%22%3A%22%7B%5C%22show_banner%5C%22%3A%20%5C%221%5C%22%2C%20%5C%22usm_so%5C%22%3A%20%5C%220%5C%22%2C%20%5C%22usm_cceg%5C%22%3A%204000%2C%20%5C%22background%5C%22%3A%20%5B%5C%22e9e8e8%5C%22%2C%20%5C%2200a9e5%5C%22%5D%2C%20%5C%22tagline%5C%22%3A%20%5C%22Discover%20the%20Joy%20of%20Lucid%20Learning%5C%22%2C%20%5C%22show_actv_key%5C%22%3A%20%5C%221%5C%22%7D%22%2C%22android_main_app_url%22%3A%22https%3A%2F%2Fplay.google.com%2Fstore%2Fapps%2Fdetails%3Fid%3Dcom.app.learningsolutions.kodemapa%26amp%3Bpcampaignid%3Dweb_share%22%2C%22url_advertise_with_us%22%3A%22%22%7D; lang=1; eg_user="2|1:0|10:1719200528|7:eg_user|48:MTszZjlmZDI3YzNmODM0YjMxOGExMjk5MTUzZmY2Yjc4Mg==|7e983b975ab2df70fabc9ee1c4460a8a584924c7a813a4babbd4e3640f4fd748"; g_state={"i_l":0,"i_t":1719286926821}',
        'Host': 'kodemapa.com',
        'Origin': 'https://kodemapa.com',
        'Referer': 'https://kodemapa.com/login',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    questions_by_section = {}
    
    try:
        for category, test_urls in test_urls_by_category.items():
            questions_by_section[category] = []
            for test_url in test_urls:
                # Complete the endpoint URL
                test_url = "/testget/" + test_url.split("p/")[1]
                full_url = f"https://kodemapa.com/api/v1/testapp{test_url}?attempt_current_test=1"
                # Make the GET request to the endpoint
                response = requests.get(full_url, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                data = response.json()  # Parse the JSON response
                
                if not data.get("status"):
                    return "Error fetching data from the endpoint", 500
                
                test_info = data['result']['data'][0]
                questions_by_section[category].extend(test_info['sec_details'][0]['sec_questions'])
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from the endpoint: {e}", 500
    except requests.exceptions.JSONDecodeError as e:
        return f"Error decoding JSON: {e}", 500
    
    if request.method == 'POST':
        selected_questions_indices = request.form.getlist('question')
        selected_questions = []

        for idx in selected_questions_indices:
            section_name, question_index = idx.split('-')
            question_index = int(question_index)
            selected_questions.append(questions_by_section[section_name][question_index])

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
        </div>
        </body>
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
                            <table>
                                <tr>
                                    <th><input type="checkbox" onclick="toggleSelectAll(this)"> Select All</th>
                                    <th>Question and Options</th>
                                    <th>Difficulty Level</th>
                                </tr>
                                {% for index, question in enumerate(questions) %}
                                <tr>
                                    <td><input type="checkbox" name="question" value="{{ section }}-{{ index }}"></td>
                                    <td>
                                        <p><strong>Question {{ index + 1 }}:</strong> {{ question['que']['1']['q_string'] | safe }}</p>
                                        <ul>
                                            {% for option in question['que']['1']['q_option'] %}
                                                <li>{{ option | safe }}</li>
                                            {% endfor %}
                                        </ul>
                                    </td>
                                    <td>{{ question.get('difficulty_level', 'N/A') }}</td>
                                </tr>
                                {% endfor %}
                            </table>
                            <label for="num_questions_{{ section }}">Number of Questions to Randomly Select:</label>
                            <input type="number" id="num_questions_{{ section }}" name="num_questions_{{ section }}">
                            <button type="button" onclick="selectRandomQuestions('{{ section }}')">Select Random Questions</button>
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
                for (let i = 0; i < numQuestions; i++) {
                    if (checkboxesArray[i]) {
                        checkboxesArray[i].checked = true;
                    }
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
                    }
                });
            }
        </script>
        </body>
        </html>
        '''
        
        return render_template_string(html_template, questions_by_section=questions_by_section, enumerate=enumerate)

if __name__ == "__main__":
    app.run(debug=True)
