import base64
import requests
from typing import Union
from django.apps import apps

class OpenAiAdapter:
    def __init__(self):
        self.api_key = apps.get_app_config('images').openai_api_key
        if self.api_key == '':
            raise ValueError('OPENAI_API_KEY not set')
        
    def prompt_image_description(self, image_file: str) -> Union[str, None]:
        try:
            response = self.make_request(self.make_image_prompt(image_file))
            
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            # log
            raise e
       
    def make_request(self, payload):
        headers =  {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response
    
    def make_image_prompt(self, image_file: str) -> dict:
        base64_image = self._encode_image(image_file)
        return {
            'model': "gpt-4-vision-preview",
            'messages': [
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "what's in this image?"},
                        {
                            "type": "image_url", 
                            "image_url": {
                                'url': f"data:image/jpg;base64,{base64_image}"
                            }
                        }
                    ],
                },
            ],
            'max_tokens': 300
        }

    
    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
