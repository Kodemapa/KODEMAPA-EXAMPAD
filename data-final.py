import json
import os
import requests

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return filename.replace(" ", "_").replace("/", "_").replace(":", "_").replace("\\", "_").replace("\t", "_").replace("\n", "_").replace("\r", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")

def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_{counter}{extension}"
        counter += 1
    return unique_filename

# Load data from local JSON file
with open('CBSE_XI.json', 'r') as file:
    data = json.load(file)['result']['data']

# Directory to save response bodies
response_body_dir = 'responseBody'

# Create directory if it doesn't exist
if not os.path.exists(response_body_dir):
    os.makedirs(response_body_dir)

# Headers for the GET request
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8,fi;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Cookie': 'G_ENABLED_IDPS=google; __stripe_mid=5348a0e2-0460-4150-b6c5-96020a471031008362; eg_user="2|1:0|10:1719584084|7:eg_user|48:MTs2YWJjMjUzMzc5OTg0ZWUxOTE0NDIyZDY2M2U0ZTc2Yg==|38139e00e495fb68c87c63732b15816c466fa053398ea122403ba06ee8387eee"; g_state={"i_l":0,"i_t":1719670483936}; client_meta=%7B%22homepage_masthead%22%3A%22%7B%5C%22show_banner%5C%22%3A%20%5C%221%5C%22%2C%20%5C%22usm_so%5C%22%3A%20%5C%220%5C%22%2C%20%5C%22usm_cceg%5C%22%3A%204000%2C%20%5C%22background%5C%22%3A%20%5B%5C%22e9e8e8%5C%22%2C%20%5C%2200a9e5%5C%22%5D%2C%20%5C%22tagline%5C%22%3A%20%5C%22Discover%20the%20Joy%20of%20Lucid%20Learning%5C%22%2C%20%5C%22show_actv_key%5C%22%3A%20%5C%221%5C%22%7D%22%2C%22android_main_app_url%22%3A%22https%3A%2F%2Fplay.google.com%2Fstore%2Fapps%2Fdetails%3Fid%3Dcom.app.learningsolutions.kodemapa%26amp%3Bpcampaignid%3Dweb_share%22%2C%22url_advertise_with_us%22%3A%22%22%7D; profile_img_url=%2Fstatic%2Fimages%2Fuser_profile.png; lang=1; website_features_status=%7B%22ft_ios_app_created%22%3A%22https%3A%2F%2Fapps.apple.com%2Fapp%2Fskill-sphere-kode-mapa%2Fid6475598680%22%2C%22ft_allow_app_theme_customisation%22%3Atrue%2C%22ft_test_security_mechanisms%22%3Atrue%2C%22ft_duplicate_video_course%22%3Atrue%2C%22ft_allow_erp%22%3A%22https%3A%2F%2Ferp.kodemapa.com%22%2C%22ft_allow_live_classes%22%3Atrue%2C%22ft_allow_homepage_customization%22%3A%22%5B%5C%221%5C%22%2C%20%5B%5C%221%5C%22%2C%20%5C%222%5C%22%5D%5D%22%2C%22ft_allow_live_class_recording%22%3Atrue%2C%22ft_disable_signup%22%3Afalse%2C%22ft_exam_calendar%22%3Afalse%2C%22show_whatsapp_contact%22%3Atrue%2C%22ft_show_news_and_current_affairs%22%3Atrue%2C%22ft_allow_e_library%22%3Atrue%2C%22ft_active_creator_mode%22%3Afalse%2C%22ft_allow_video_course%22%3Atrue%7D',
    'Referer': 'https://kodemapa.com/login',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

# Track missing files
missing_files = []

# Iterate through all the L4 categories and their L5 tests
for l3_category in data['L3']:
    for l4_category in l3_category['L4']:
        for test in l4_category['L5']:
            test_url = test[5]
            test_url_part = test_url.split("p/")[1]
            file_name = f"{l4_category['name']}_{test[0]}.json"
            sanitized_file_name = sanitize_filename(file_name)
            unique_file_name = get_unique_filename(response_body_dir, sanitized_file_name)
            file_path = os.path.join(response_body_dir, unique_file_name)
            
            # Always fetch the data from the server
            full_url = f"https://kodemapa.com/api/v1/testapp/testget/{test_url_part}?attempt_current_test=1"
            try:
                response = requests.get(full_url, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                response_data = response.json()  # Parse the JSON response
                
                # Ensure the response status is true
                if response_data.get("status"):
                    # Save the response body to the file
                    with open(file_path, 'w') as f:
                        json.dump(response_data, f)
                    
                    # Add the new attribute to the test with the path of the newly created file
                    test.append({"file_path": file_path})
                    print(f"Fetched and saved data, appended file path to test: {file_path}")
                else:
                    print(f"Error: Status false for URL {full_url}")
            
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {full_url}: {e}")
            except requests.exceptions.JSONDecodeError as e:
                print(f"Error decoding JSON from {full_url}: {e}")

# Save the updated data back to the JSON file
updated_data = {'result': {'data': data}}
with open('CBSE_XI.json', 'w') as file:
    json.dump(updated_data, file, indent=4)

print("Process completed successfully.")
if missing_files:
    print(f"Missing files: {missing_files}")
