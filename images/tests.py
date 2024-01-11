from django.test import TestCase
from .models import Image
import datetime
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, patch
from images import actions
import base64

# View Tests
class ImageIndexEndpointTest(TestCase):
    fixtures = ['images.json']

    def test_it_returns_a_paginated_list_of_image_records(self):
        """
        It should return a paginated list of image records
        """
        rsp = self.client.get("/images/")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(len(rsp.json()), 3)
        self.assertEqual([1,2,3], [i['id'] for i in rsp.json()])

class ImageShowEndpointTest(TestCase):
    fixtures = ['images.json']

    def test_if_image_not_found_it_responds_w_404(self):
        """
        If the image is not found it should respond with a 404
        """
        self.assertEqual(self.client.get("/images/4").status_code, 404)

    def test_it_returns_the_image_record_if_found(self):
        """
        If the image is found it returns the image metadata
        """

        rsp = self.client.get("/images/1")
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(
            rsp.json(), 
            {
                "id": 1,
                "file_path": f"/{settings.MEDIA_ROOT}/some_test_file.jpg",
                "description": "this is a description for image 1",
                "analyzed": True,
            }
        )

class ImageCommentsEndpoingTest(TestCase):
    fixtures = ['images.json', 'comments']

    def test_if_image_not_found_it_responds_w_404(self):
        """
        If the image is not found it responds with a 404
        """
        self.assertEqual(self.client.get("/images/4").status_code, 404)

    def test_if_image_is_found_and_has_no_comments_it_returns_an_empty_json_array(self):
        """
        If the image is found, but has no comments it responds with an empty list
        """
        rsp = self.client.get('/images/2/comments')
        self.assertEqual(rsp.json(), [])

    def test_if_image_is_found_and_has_comments_it_returns_a_json_array_of_paginated_comments(self):
        """
        If the image is found and has comments, it responds with a paginated list of comments
        """
        rsp = self.client.get('/images/1/comments')
        self.assertEqual(len(rsp.json()), 3)

class ImageAnalyzeEndpointTest(TestCase):
    def test_if_the_request_method_is_get_it_responds_with_405(self):
        rsp = self.client.get('/images/analyze')
        self.assertEqual(rsp.status_code, 405)
        
    def test_it_validates_a_file_is_uploaded(self):
        rsp = self.client.post('/images/analyze', data={'file_path': ''})
        self.assertEqual(rsp.status_code, 422)
        self.assertEqual(rsp.json(), {'file_path': ['This field is required.']})

    def test_it_validates_the_uploaded_file_is_an_image(self):
        non_image_file = SimpleUploadedFile("non_image.xlsx", b"file_content", content_type="application/vnd.ms-excel")
        rsp = self.client.post('/images/analyze', data={'file_path': non_image_file})
        self.assertContains(rsp, 'Upload a valid image.', status_code=422)

    @patch('images.actions.store_and_analyze_image')
    def test_if_an_image_file_is_uploaded_it_calls_create_and_analyze_image(self, action_mock):
        """
        If the user uploads a valid image, the view runs the store_and_analyze_image action
        """

        action_mock.return_value = Image(id=1)

        image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAUA" + "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO" + "9TXL0Y4OHwAAAABJRU5ErkJggg==")
        image_file = SimpleUploadedFile("image_file.png", image_data, content_type="image/png")

        rsp = self.client.post('/images/analyze', data={'file_path': image_file})
        self.assertEqual(rsp.status_code, 200)
        action_mock.assert_called()
        self.assertEqual(rsp.json()['image']['id'], 1)
        print(rsp.json())

        


# Model Tests
class ImageModelTests(TestCase):

    def test_analyzed_is_True_if_analyzed_at_not_None(self):
        image = Image(analyzed_at=datetime.datetime.now())

        self.assertIs(image.analyzed, True)

    def test_analyzed_is_False_if_analyzed_at_isNone(self):
        image = Image()

        self.assertIs(image.analyzed, False)