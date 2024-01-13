"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from abc import ABC, abstractmethod
from typing import Union
import logging
from django.conf import settings
from django.apps import apps
from .openai_adapter import OpenAiAdapter, OpenAIError

class ImageDescriberError(Exception):...

class ImageDescriber(ABC):
    @abstractmethod
    def describe_image(self, image_file: str) -> Union[str, None]:
        ...

class DummyDescriber(ImageDescriber):
    def describe_image(self, image_file: str) -> Union[str, None]:
        return f"A description for {image_file}"

class OpenAIDescriber(ImageDescriber):
    def describe_image(self, image_file: str) -> Union[str, None]:
        try:
            adapter = OpenAiAdapter()
            return adapter.prompt_image_description(image_file)
        except OpenAIError as e:
            logging.warn(e)
            ImageDescriberError(message = str(e))

    
def make_image_describer():
    if apps.get_app_config('images').openai_api_key == '':
        return DummyDescriber()
    
    return OpenAIDescriber()