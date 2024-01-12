from django.apps import apps
from django.test import TestCase
from ..openai_adapter import OpenAiAdapter
from unittest.mock import patch
import json
import base64
import os
import requests

base64image = "iVBORw0KGgoAAAANSUhEUgAAAAUA" + "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO" + "9TXL0Y4OHwAAAABJRU5ErkJggg=="
def create_test_file(file_name=None):
    file_name = file_name or '/tmp/test-image-file.png'
    image_data = base64.b64decode(base64image)
    with open(file_name, 'wb') as image_file:
        image_file.write(image_data)
    
    return file_name

class OpenAiAdapterInstantiationTest(TestCase):
    def test_it_raises_a_value_error_if_api_key_blank(self):
        apps.get_app_config('images').openai_api_key = ''
        
        self.assertRaises(ValueError, OpenAiAdapter)

    def test_it_instantiates_the_adapter_if_api_key_is_not_blank(self):
        apps.get_app_config('images').openai_api_key = 'some-test-key'
        
        self.assertIsInstance(OpenAiAdapter(), OpenAiAdapter)
        
class OpenAiAdapterMakeRequestTest(TestCase):
    def setUp(self):
        apps.get_app_config('images').openai_api_key = 'some-random-key'
        self.adapter = OpenAiAdapter()

    @patch('requests.post')
    def test_it_makes_a_request_to_openai_with_default_headers_and_payload(self, post_mock):
        payload = {"key": "value"}
        
        self.adapter.make_request(payload)
        
        post_mock.expect_called_with(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {apps.get_app_config('images').openai_api_key}"
            }, 
            payload=payload)
        
class OpenAiAdapterMakeImagePromptTest(TestCase):
    def setUp(self):
        apps.get_app_config('images').openai_api_key = 'some-api-key'
        self.adapter = OpenAiAdapter()
        
    def test_it_builds_an_image_prompt_with_the_image_from_the_file(self):
        test_image_path = create_test_file()
        prompt_dict = self.adapter.make_image_prompt(image_file=test_image_path)
        
        self.assertEqual(prompt_dict, {
            'model': "gpt-4-vision-preview",
            'messages': [
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "what's in this image?"},
                        {
                            "type": "image_url", 
                            "image_url": {
                                'url': f"data:image/jpg;base64,{base64image}"
                            }
                        }
                    ],
                },
            ],
            'max_tokens': 300
        })

class OpenAiAdapterPromptImageDescriptionTest(TestCase):
    def setUp(self):
        apps.get_app_config('images').openai_api_key = 'some-random-key'

    @patch('images.openai_adapter.OpenAiAdapter.make_request')
    def test_prompt_image_description_makes_request_with_correct_payload_and_returns_description(self, requester_mock):
        """
        When prompt_image_description is called it makes a request to 
        """
        test_response = requests.Response()
        test_response._content = b'{ "choices":[ { "message": { "content": "some content" } } ]}'
        requester_mock.return_value = test_response
        
        # Need to create an image file and store it.
        image_file_path = create_test_file()
        self.assertTrue(os.path.isfile(image_file_path))

        
        adapter = OpenAiAdapter()
        description = adapter.prompt_image_description(image_file_path)
        
        self.assertEqual(description, "some content")
        self.assertEqual(test_response, requester_mock.return_value)
        requester_mock.was_called_with(adapter.make_image_prompt(image_file_path))
        
        os.remove(image_file_path)
        
        

        
        