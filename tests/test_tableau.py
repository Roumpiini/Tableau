import unittest
from unittest.mock import patch, MagicMock
import sys
# sys.path.append("./.venv/lib/python3.9/site-packages")
import base64
import requests
import xml.etree.ElementTree as ET
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tableau import authenticate_tableau, get_user_id, get_user_title_from_freshservice, add_user_to_group
class TestScript(unittest.TestCase):

    @patch('requests.post')
    def test_authenticate_tableau_success(self, mock_post):
        # Mock response from Tableau auth
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
            <tsResponse xmlns="http://tableau.com/api" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <credentials token="test_token"/>
            </tsResponse>
        """
        mock_post.return_value = mock_response

        # Call function under test
        token = authenticate_tableau()

        # Assertions
        self.assertEqual(token, "test_token")

    @patch('requests.get')
    def test_get_user_id_success(self, mock_get):
        # Mock response from Tableau API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = """
            <tsResponse xmlns="http://tableau.com/api" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <user id="123" name="testuser"/>
            </tsResponse>
        """
        mock_get.return_value = mock_response

        # Call function under test
        user_id = get_user_id("testuser", "test_token")

        # Assertions
        self.assertEqual(user_id, "123")

    @patch('requests.get')
    def test_get_user_title_from_freshservice_success(self, mock_get):
        # Mock response from Freshservice API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [{"job_title": "Enterprise IT Technician"}]
        }
        mock_get.return_value = mock_response

        # Call function under test
        title = get_user_title_from_freshservice("testuser@domain.com")

        # Assertions
        self.assertEqual(title, "Enterprise IT Technician")

    @patch('requests.post')
    def test_add_user_to_group_success(self, mock_post):
        # Mock response from Tableau API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Call function under test
        add_user_to_group("testuser@domain.com", "IT", "test_token")

        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()

