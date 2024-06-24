import json
import os
import requests

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    return filename.replace(" ", "_").replace("/", "_").replace(":", "_").replace("\\", "_").replace("\t", "_").replace("\n", "_").replace("\r", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")

# Load data from local JSON file
with open('CBSE_XII.json', 'r') as file:
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
    'Cookie': '_sp_id.7892=b71b3632-9dca-4f89-b2c3-72cb35c1cc54.1714797513.1.1714797513..4c8a20ae-d9d3-4ad4-8d90-7d501845781a....0; _fbp=fb.1.1715998812504.413542895; G_ENABLED_IDPS=google; eg_user="2|1:0|10:1719207352|7:eg_user|48:MTszMmE3MGUxNTg1ZDM0YzlmYTg0MzlhODNlMTE2OTk3YQ==|b4b2000c19b8534e638d27053fd448a0ddcb34bc9f0e7778cbdc9867f83ea82a"; g_state={"i_l":0,"i_t":1719293753553}; profile_img_url=%2Fstatic%2Fimages%2Fuser_profile.png; lang=1; client_meta=%7B%22homepage_masthead%22%3A%22%7B%5C%22show_banner%5C%22%3A%20%5C%221%5C%22%2C%20%5C%22usm_so%5C%22%3A%20%5C%220%5C%22%2C%20%5C%22usm_cceg%5C%22%3A%204000%2C%20%5C%22background%5C%22%3A%20%5B%5C%22e9e8e8%5C%22%2C%20%5C%2200a9e5%5C%22%5D%2C%20%5C%22tagline%5C%22%3A%20%5C%22Discover%20the%20Joy%20of%20Lucid%20Learning%5C%22%2C%20%5C%22show_actv_key%5C%22%3A%20%5C%221%5C%22%7D%22%2C%22android_main_app_url%22%3A%22https%3A%2F%2Fplay.google.com%2Fstore%2Fapps%2Fdetails%3Fid%3Dcom.app.learningsolutions.kodemapa%26amp%3Bpcampaignid%3Dweb_share%22%2C%22url_advertise_with_us%22%3A%22%22%7D',
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
            file_path = os.path.join(response_body_dir, sanitized_file_name)
            
            if os.path.exists(file_path):
                try:
                    # Read the response body from the saved file
                    with open(file_path, 'r') as f:
                        response_data = json.load(f)
                    
                    # Ensure the response status is true
                    if response_data.get("status"):
                        # Add the new attribute to the test with the path of the newly created file
                        test.append({"file_path": file_path})
                        print(f"Appended file path to test: {file_path}")
                    else:
                        print(f"Error: Status false in file {file_path}")
                
                except (OSError, json.JSONDecodeError) as e:
                    print(f"Error reading or parsing file {file_path}: {e}")
            else:
                # File does not exist, make a GET request to fetch the data
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
with open('CBSE_XII.json', 'w') as file:
    json.dump(updated_data, file, indent=4)

print("Process completed successfully.")
if missing_files:
    print(f"Missing files: {missing_files}")
