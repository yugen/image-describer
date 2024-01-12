from ..models import Image
from django.test import TestCase
import datetime

class ImageModelTests(TestCase):

    def test_analyzed_is_True_if_analyzed_at_not_None(self):
        image = Image(analyzed_at=datetime.datetime.now())

        self.assertIs(image.analyzed, True)

    def test_analyzed_is_False_if_analyzed_at_isNone(self):
        image = Image()

        self.assertIs(image.analyzed, False)