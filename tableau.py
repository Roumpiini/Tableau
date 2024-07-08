import sys
# sys.path.append("./.venv/lib/python3.9/site-packages")
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
import base64
import requests
import json
import xml.etree.ElementTree as ET

BASE_URL = os.getenv("TABLEAU_BASE_URL")
API_VERSION = os.getenv("TABLEAU_API_VERSION")
SITE_ID = os.getenv("TABLEAU_SITE_ID")
USERNAME = os.getenv("TABLEAU_USERNAME")
PASSWORD = os.getenv("TABLEAU_PASSWORD")

FRESHSERVICE_BASE_URL = os.getenv("FRESHSERVICE_BASE_URL")
FRESHSERVICE_API_KEY = os.getenv("FRESHSERVICE_API_KEY")

# Encode the API key for Basic Authentication
encoded_api_key = base64.b64encode(FRESHSERVICE_API_KEY.encode('utf-8')).decode('utf-8')
FRESHSERVICE_HEADERS = {
    "Authorization": f"Basic {encoded_api_key}",
    "Content-Type": "application/json"
}

def authenticate_tableau():
    url = f"{BASE_URL}/api/{API_VERSION}/auth/signin"
    payload = f"""
    <tsRequest>
        <credentials name="{USERNAME}" password="{PASSWORD}">
            <site id="{SITE_ID}"/>
        </credentials>
    </tsRequest>
    """
    headers = {
        "Content-Type": "application/xml"
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        token = root.find('.//{http://tableau.com/api}credentials').get('token')
        return token

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def get_user_id(username, token):
    url = f"{BASE_URL}/api/{API_VERSION}/sites/{SITE_ID}/users"
    headers = {
        "X-Tableau-Auth": token,
        "Content-Type": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.text:
            root = ET.fromstring(response.content)
            for user_elem in root.findall('.//{http://tableau.com/api}user'):
                if user_elem.get('name') == username:
                    return user_elem.get('id')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def create_user_in_tableau(username, token):
    url = f"{BASE_URL}/api/{API_VERSION}/sites/{SITE_ID}/users"
    headers = {
        "X-Tableau-Auth": token,
        "Content-Type": "application/xml"
    }
    payload = f"""
    <tsRequest>
        <user name="{username}" siteRole="Viewer"/>
    </tsRequest>
    """

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        user_id = root.find('.//{http://tableau.com/api}user').get('id')
        return user_id

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def get_user_title_from_freshservice(email):
    url = f"{FRESHSERVICE_BASE_URL}/agents?email={email}"

    try:
        response = requests.get(url, headers=FRESHSERVICE_HEADERS)
        response.raise_for_status()

        if response.json():
            data = response.json()
            if 'agents' in data and data['agents']:
                return data['agents'][0].get('job_title')

        # Agent vs Requestor
        url = f"{FRESHSERVICE_BASE_URL}/requesters"
        params = {
            'email': email
        }
        response = requests.get(url, headers=FRESHSERVICE_HEADERS, params=params)
        response.raise_for_status()
        requester_data = response.json().get('requesters', [])

        if requester_data:
            return requester_data[0].get('job_title')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None


def get_group_id(group_name, token):
    url = f"{BASE_URL}/api/{API_VERSION}/sites/{SITE_ID}/groups"
    headers = {
        "X-Tableau-Auth": token,
        "Content-Type": "application/xml"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if response.text:
            root = ET.fromstring(response.content)
            for group_elem in root.findall('.//{http://tableau.com/api}group'):
                if group_elem.get('name') == group_name:
                    return group_elem.get('id')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def add_user_to_group(user_id, group_id, token):
    url = f"{BASE_URL}/api/{API_VERSION}/sites/{SITE_ID}/groups/{group_id}/users"
    headers = {
        "X-Tableau-Auth": token,
        "Content-Type": "application/xml"
    }
    payload = f"""
    <tsRequest>
        <user id="{user_id}"/>
    </tsRequest>
    """

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        print(f"User '{user_id}' added successfully to group '{group_id}'.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

def get_requester_email_from_ticket(ticket_id):
    url = f"{FRESHSERVICE_BASE_URL}/tickets/{ticket_id}"

    try:
        response = requests.get(url, headers=FRESHSERVICE_HEADERS)
        response.raise_for_status()
        ticket_data = response.json()

        requester_id = ticket_data['ticket']['requester_id']
        print(f"Requester ID: {requester_id}")  # Debug

        requester_url = f"{FRESHSERVICE_BASE_URL}/requesters/{requester_id}"
        print(f"Requester URL: {requester_url}")  # Debug

        response = requests.get(requester_url, headers=FRESHSERVICE_HEADERS)
        response.raise_for_status()
        requester_data = response.json()
        print(f"Requester Data: {json.dumps(requester_data, indent=4)}")  # Debug

        if 'requester' in requester_data:
            return requester_data['requester'].get('primary_email')

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as err:
        print(f"Other error occurred: {err}")

    return None

def main():
    try:
        # Example
        ticket_id = 50022
        email = get_requester_email_from_ticket(ticket_id)
        if email:
            title = get_user_title_from_freshservice(email)
            token = authenticate_tableau()
            if token:
                user_id = get_user_id(email, token)
                if not user_id:
                    user_id = create_user_in_tableau(email, token)
                    if user_id:
                        print(f"User '{email}' created successfully in Tableau with ID '{user_id}'.")
                    else:
                        print(f"Failed to create user '{email}' in Tableau.")
                        return
                group_name = None

                if title == "Director, Customer Success":
                    group_name = "CS Directors"
                elif title == "Manager, Customer Success":
                    group_name = "CS Manager"
                elif title == "Customer Success Manager":
                    group_name = "CSMs"

                if group_name:
                    group_id = get_group_id(group_name, token)
                    if group_id:
                        add_user_to_group(user_id, group_id, token)
                    else:
                        print(f"Group '{group_name}' not found.")
                else:
                    print(f"No group defined for title '{title}'.")
            else:
                print("Failed to authenticate with Tableau.")
        else:
            print(f"Could not find requester email for ticket ID '{ticket_id}'.")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

