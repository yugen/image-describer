from unittest.mock import patch

from django.apps import apps
from django.test import TestCase

from ..describers  import ImageDescriber, DummyDescriber, OpenAIDescriber, make_image_describer

class DummyDescriberTest(TestCase):
    def setUp(self):
        self.describer = DummyDescriber()
        
    def test_it_is_an_instance_of_ImageDescriber(self):
        self.assertIsInstance(self.describer, ImageDescriber)
        
    def test_it_returns_a_dummy_description_string_for_an_image_at_path(self):
        self.assertIsInstance(self.describer.describe_image('any_path.png'), str)
class OpenAIDescriberTest(TestCase):
    def setUp(self):
        # Set open_api_key to empty string so we don't accidentally make calls
        apps.get_app_config('images').openai_api_key = 'some-random-key'
        self.describer = OpenAIDescriber()
        
    def test_it_is_an_instance_of_ImageDescriber(self):
        self.assertIsInstance(self.describer, ImageDescriber)
        
    @patch('images.openai_adapter.OpenAiAdapter.prompt_image_description')
    def test_it_calls_OpenAIAdapter__describe_image_when_describing_image(self, adapter_method_mock):
        """
        The OpenAIDescriber.describe_image should call OpenAiAdapter.prompt_image_description
        """
        adapter_method_mock.return_value = 'This is a description of the image from OpenAI'
        
        image_path = 'some_image_path.jpg'
        description = self.describer.describe_image(image_path)
        
        adapter_method_mock.assert_called_with(image_path)
        self.assertEqual(description, adapter_method_mock.return_value)
class ImageDescriberFactoryTest(TestCase):
    def test_if_open_api_key_is_blank_it_should_return_DummyDescriber(self):
        apps.get_app_config('images').openai_api_key = ''
        
        self.assertIsInstance(make_image_describer(), DummyDescriber)
        
    def test_if_open_api_key_is_not_blank_it_should_return_OpenAPIDescriber(self):
        apps.get_app_config('images').openai_api_key = 'some-api-key'
        
        self.assertIsInstance(make_image_describer(), OpenAIDescriber)
