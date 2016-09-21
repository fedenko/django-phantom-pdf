import os
from django.test import TestCase, LiveServerTestCase, override_settings
from selenium.webdriver.phantomjs.webdriver import WebDriver
import phantom_pdf

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))

class TestPhantomPDFSettings(TestCase):

    @override_settings(
        PHANTOMJS_GENERATE_PDF=os.path.join(BASE_DIR, "generate_pdf.js"),
        PHANTOMJS_PDF_DIR="/tmp/phantom_pdf_test/pdfs",
        PHANTOMJS_BIN=os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"),
        PHANTOMJS_ACCEPT_LANGUAGE="en, uk",
        PHANTOMJS_ORIENTATION="landscape",
        PHANTOMJS_MARGIN="1cm",
        PHANTOMJS_FORMAT="A4",
        KEEP_PDF_FILES=True
    )
    def test_old_settings(self):
        request_to_pdf = phantom_pdf.RequestToPDF()
        self.assertEqual(request_to_pdf.PHANTOMJS_GENERATE_PDF, os.path.join(BASE_DIR, "generate_pdf.js"))
        self.assertEqual(request_to_pdf.PHANTOMJS_PDF_DIR, "/tmp/phantom_pdf_test/pdfs")
        self.assertEqual(request_to_pdf.PHANTOMJS_BIN, os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"))
        self.assertEqual(request_to_pdf.PHANTOMJS_ACCEPT_LANGUAGE, "en, uk")
        self.assertEqual(request_to_pdf.PHANTOMJS_ORIENTATION, "landscape")
        self.assertEqual(request_to_pdf.PHANTOMJS_MARGIN, "1cm")
        self.assertEqual(request_to_pdf.PHANTOMJS_FORMAT, "A4")
        self.assertEqual(request_to_pdf.KEEP_PDF_FILES, True)


    @override_settings(
        PHANTOMJS_GENERATE_PDF=os.path.join(BASE_DIR, "generate_pdf.js"),
        PHANTOMJS_PDF_DIR="/tmp/phantom_pdf_test/pdfs",
        PHANTOMJS_BIN=os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"),
        PHANTOMJS_ACCEPT_LANGUAGE="en, uk",
        PHANTOMJS_PAPER_SIZE={
            "format": "A4",
            "orientation": "portrait",
            "margin": "1.5cm",
            "footer":{
                "height": "1cm",
                "contents": "<p>Footer <span style='float:right'>{{page_num}}/{{num_pages}}</span></p>"
            }
        },
        KEEP_PDF_FILES=True
    )
    def test_new_settings(self):
        request_to_pdf = phantom_pdf.RequestToPDF()
        self.assertEqual(request_to_pdf.PHANTOMJS_GENERATE_PDF, os.path.join(BASE_DIR, "generate_pdf.js"))
        self.assertEqual(request_to_pdf.PHANTOMJS_PDF_DIR, "/tmp/phantom_pdf_test/pdfs")
        self.assertEqual(request_to_pdf.PHANTOMJS_BIN, os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"))
        self.assertEqual(request_to_pdf.PHANTOMJS_ACCEPT_LANGUAGE, "en, uk")
        self.assertEqual(request_to_pdf.PHANTOMJS_PAPER_SIZE, {
            "format": "A4",
            "orientation": "portrait",
            "margin": "1.5cm",
            "footer":{
                "height": "1cm",
                "contents": "<p>Footer <span style='float:right'>{{page_num}}/{{num_pages}}</span></p>"
            }
        })
        self.assertEqual(request_to_pdf.KEEP_PDF_FILES, True)

class TestPhantomPDF(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPhantomPDF, cls).setUpClass()
        cls.selenium = WebDriver(executable_path=os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"))
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TestPhantomPDF, cls).tearDownClass()


    @override_settings(
        PHANTOMJS_GENERATE_PDF=os.path.join(BASE_DIR, "generate_pdf.js"),
        PHANTOMJS_PDF_DIR="/tmp/phantom_pdf_test/pdfs",
        PHANTOMJS_BIN=os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"),
        PHANTOMJS_ACCEPT_LANGUAGE="en, uk",
        PHANTOMJS_PAPER_SIZE={
            "format": "A4",
            "orientation": "portrait",
            "margin": "1.5cm",
            "footer":{
                "height": "1cm",
                "contents": "<p>Footer <span style='float:right'>{{page_num}}/{{num_pages}}</span></p>"
            }
        },
        KEEP_PDF_FILES=True
    )
    def test_something(self):
        request_to_pdf = phantom_pdf.RequestToPDF()
