import json
import os
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase, LiveServerTestCase, override_settings
from django.utils.http import urlencode
from django.utils import six
if six.PY3:
    from pdfminer.pdfparser import PDFParser, PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import PDFPageAggregator
    from pdfminer.layout import LAParams, LTTextBox, LTTextLine
else:
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
import mock
import phantom_pdf
import PyPDF2

DPI = 72

A4 = 210, 297 #mm

A4_DPI = tuple(map(lambda mm: round((mm * DPI) / 25.4), A4))

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))

if six.PY3:
    def convert(infile):
        parser = PDFParser(infile)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        extracted_text = ''

        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text += lt_obj.get_text()
        return extracted_text
else:
    def convert(infile):
        output = six.StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)

        for page in PDFPage.get_pages(infile):
            interpreter.process_page(page)
        converter.close()
        text = output.getvalue()
        output.close
        return text

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

class TestPhantomPDFSubprocess(TestCase):


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
    @mock.patch("phantom_pdf.generator.subprocess.Popen")
    @mock.patch.object(phantom_pdf.RequestToPDF, "_return_response")
    def test_subprocess(self, mock_return_response, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {
            'wait.return_value': 0
        }
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        mock_return_response.return_value = HttpResponse()

        response = self.client.get("{url}?{params}".format(
            url=reverse('index'),
            params=urlencode({"format":"pdf"})
        ))
        self.assertTrue(mock_subproc_popen.called)
        command = mock_subproc_popen.call_args[0][0]
        self.assertEqual(command[0], os.path.join(os.path.dirname(BASE_DIR), "node_modules", "phantomjs-prebuilt", "bin", "phantomjs"))
        self.assertEqual(command[1], "--ssl-protocol=ANY")
        self.assertEqual(command[2], os.path.join(BASE_DIR, "generate_pdf.js"))
        self.assertEqual(command[4], "/tmp/phantom_pdf_test/pdfs/test.pdf")
        self.assertEqual(command[6], "en, uk")
        self.assertEqual(json.loads(command[7]), {
            "format": "A4",
            "orientation": "portrait",
            "margin": "1.5cm",
            "footer":{
                "height": "1cm",
                "contents": "<p>Footer <span style='float:right'>{{page_num}}/{{num_pages}}</span></p>"
            }
        })

class TestPhantomPDF(LiveServerTestCase):

    @override_settings(
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
    @mock.patch.object(phantom_pdf.RequestToPDF, "_build_url")
    def test_view(self, mock_build_url):
        mock_build_url.return_value = "{host}{url}".format(
            host=self.live_server_url,
            url=reverse('index')
        )
        response = self.client.get("{host}{url}?{params}".format(
            host=self.live_server_url,
            url=reverse('index'),
            params=urlencode({"format":"pdf"})
        ))
        pdf_file = six.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        self.assertEqual(pdf_reader.getNumPages(), 5)
        for page in pdf_reader.pages:
            self.assertEqual(page.mediaBox.lowerLeft, (0,0))
            self.assertEqual(page.mediaBox.upperRight, A4_DPI)
