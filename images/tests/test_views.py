import base64
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..models import Image

# View Tests
class ImageIndexEndpointTest(TestCase):
    fixtures = ['images.json']

    def setUp(self):
        """
        Set the image_page_size to test pagination without creating lots of image records
        """
        apps.get_app_config('images').image_page_size = 2

    def test_if_no_page_is_provided_it_returns_the_first_page_of_images(self):
        """
        If no page is param is provided, it should return the first page of images
        """
        rsp = self.client.get("/images/")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual([1,2], [i['id'] for i in rsp.json()['data']])
        self.assertEqual(1, int(rsp.json()['current_page']))
        self.assertEqual(2, int(rsp.json()['num_pages']))

    def test_if_page_is_provided_it_returns_that_page_of_images(self):
        """
        If a page param is provided, it should return that page of images
        """
        rsp = self.client.get("/images/?page=2")

        self.assertEqual(rsp.status_code, 200)
        self.assertEqual([3], [i['id'] for i in rsp.json()['data']])
        self.assertEqual(2, int(rsp.json()['current_page']))
        self.assertEqual(2, int(rsp.json()['num_pages']))
        
    def test_if_page_is_out_of_range_returns_a_416_response(self):
        """
        If the provided page is out of range it should return a 416 response code
        """
        rsp = self.client.get("/images/?page=3")

        self.assertEqual(rsp.status_code, 416)
        self.assertEqual(2, int(rsp.json()['num_pages']))

class ImageShowWithCommentsEndpointTest(TestCase):
    fixtures = ['images', 'comments']
    
    def test_if_image_not_found_it_responds_w_404(self):
        """
        If the image is not found it should respond with a 404
        """
        self.assertEqual(self.client.get("/image/4").status_code, 404)
        
    def test_if_image_found_and_has_no_comments_it_returns_empty_comments_array(self):
        rsp = self.client.get('/image/2')
        self.assertEqual(rsp.json()['id'], 2)
        self.assertEqual(rsp.json()['comments']['data'], [])
        
    def test_if_image_found_and_has_comments_and_no_comment_page_given_responds_with_first_page(self):
        apps.get_app_config('images').comment_page_size = 2
        rsp = self.client.get('/image/1')
        self.assertEqual(rsp.json()['id'], 1)
        self.assertEqual(rsp.json()['comments']['current_page'], 1)
        self.assertEqual(len(rsp.json()['comments']['data']), 2)
        self.assertEqual(rsp.json()['comments']['num_pages'], 2)

    def test_if_image_found_and_has_comments_and_comment_page_given_responds_with_given_page(self):
        apps.get_app_config('images').comment_page_size = 2
        rsp = self.client.get('/image/1?comment_page=2')
        self.assertEqual(rsp.json()['id'], 1)
        self.assertEqual(rsp.json()['comments']['current_page'], 2)
        self.assertEqual(len(rsp.json()['comments']['data']), 1)
        self.assertEqual(rsp.json()['comments']['num_pages'], 2)
    
    def test_if_imag_found_and_given_comment_page_is_out_of_range_responds_with_416(self):
        apps.get_app_config('images').comment_page_size = 2
        rsp = self.client.get('/image/1?comment_page=99')
        self.assertEqual(rsp.status_code, 416)

class ImageAnalyzeEndpointTest(TestCase):
    def test_if_the_request_method_is_get_it_responds_with_405(self):
        rsp = self.client.get('/analyze-image')
        self.assertEqual(rsp.status_code, 405)
        
    def test_it_validates_a_file_is_uploaded(self):
        rsp = self.client.post('/analyze-image', data={})
        self.assertEqual(rsp.status_code, 422)
        self.assertEqual(rsp.json(), {'errors': {'file': ['No file was submitted.']}})

    def test_it_validates_the_uploaded_file_is_an_image(self):
        non_image_file = SimpleUploadedFile("non_image.xlsx", b"file_content", content_type="application/vnd.ms-excel")
        rsp = self.client.post('/analyze-image', data={'file': non_image_file})
        self.assertContains(rsp, 'Upload a valid image.', status_code=422)

    @patch('images.actions.analyze_image')
    def test_if_an_image_file_is_uploaded_it_calls_create_and_analyze_image(self, action_mock):
        """
        If the user uploads a valid image, the view runs the store_and_analyze_image action
        """

        action_mock.return_value = Image(id=1)

        image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAUA" + "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO" + "9TXL0Y4OHwAAAABJRU5ErkJggg==")
        image_file = SimpleUploadedFile("image_file.png", image_data, content_type="image/png")

        rsp = self.client.post('/analyze-image', data={'file': image_file})
        
        self.assertEqual(rsp.status_code, 200)
        action_mock.assert_called()
        self.assertEqual(rsp.json()['id'], 1)
        
class AddCommentEndpointTest(TestCase):
    fixtures = ['images']

    def test_if_image_not_found_return_404(self):
        rsp = self.client.post('/image/999/comments')
        self.assertEqual(rsp.status_code, 404)

    def test_if_image_is_found_and_data_is_valid(self):
        content = 'This is a comment'
        rsp = self.client.post('/image/1/comments', data={ 'content': content })
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.json()['content'], content)
        self.assertEqual(rsp.json()['image_id'], 1)

    def test_if_image_is_found_and_data_is_not_valid_it_responds_with_errors(self):
        rsp = self.client.post('/image/1/comments')
        self.assertEqual(rsp.status_code, 422)
        self.assertIn('content', rsp.json()['errors'])

    def test_if_image_is_found_and_data__valid_it_creates_and_responds_with_new_comment(self):
        # Test the restful endpoint
        rsp = self.client.post('/image/1/comments', {"content": 'This is content'})
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.json()['content'], 'This is content')
        self.assertIsNotNone(rsp.json()['id'])

        # Test the mandated endpoint
        rsp = self.client.post('/image/1/comments', {"content": 'This is content'})
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(rsp.json()['content'], 'This is content')
        self.assertIsNotNone(rsp.json()['id'])
        
