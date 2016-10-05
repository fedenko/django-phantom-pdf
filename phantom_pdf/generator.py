# -*- coding: utf-8 -*-
import logging
from subprocess import Popen, STDOUT, PIPE
import os
import phantom_pdf_bin
import uuid

from django.conf import settings
from django.http import HttpResponse

from phantom_pdf.compat import json, urlsplit

logger = logging.getLogger(__name__)


# Path to generate_pdf.js file. Its distributed with this django app.
GENERATE_PDF_JS = os.path.join(os.path.dirname(phantom_pdf_bin.__file__),
                               'generate_pdf.js')
PHANTOM_ROOT_DIR = '/tmp/phantom_pdf'
DEFAULT_SETTINGS = dict(
    PHANTOMJS_COOKIE_DIR=os.path.join(PHANTOM_ROOT_DIR, 'cookies'),
    PHANTOMJS_GENERATE_PDF=GENERATE_PDF_JS,
    PHANTOMJS_PDF_DIR=os.path.join(PHANTOM_ROOT_DIR, 'pdfs'),
    PHANTOMJS_BIN='phantomjs',
    PHANTOMJS_ACCEPT_LANGUAGE='en',
    PHANTOMJS_FORMAT='A4',
    PHANTOMJS_ORIENTATION='landscape',
    PHANTOMJS_MARGIN=0,
    PHANTOMJS_PAPER_SIZE={},
    PHANTOMJS_VIEWPORT_SIZE={},
    PHANTOMJS_COMPENSATE_FOR_V2_PDF_RENDERING_BUG=None,
    KEEP_PDF_FILES=False,
)


class RequestToPDF(object):
    """Class for rendering a requested page to a PDF."""

    def __init__(self,
                 PHANTOMJS_COOKIE_DIR=None,
                 PHANTOMJS_PDF_DIR=None,
                 PHANTOMJS_BIN=None,
                 PHANTOMJS_GENERATE_PDF=None,
                 KEEP_PDF_FILES=None):
        """Arguments:
            PHANTOMJS_COOKIE_DIR = Directory where the temp cookies will be saved.
            PHANTOMJS_PDF_DIR = Directory where you want to the PDF to be saved temporarily.
            PHANTOMJS_BIN = Path to PhantomsJS binary.
            PHANTOMJS_GENERATE_PDF = Path to generate_pdf.js file.
            KEEP_PDF_FILES = Option to not delete the PDF file after rendering it.
            PHANTOMJS_FORMAT = Page size to use.
            PHANTOMJS_ORIENTATION = How the page will be positioned when printing.
            PHANTOMJS_MARGIN = The margins of the PDF.
        """
        self.PHANTOMJS_COOKIE_DIR = PHANTOMJS_COOKIE_DIR
        self.PHANTOMJS_PDF_DIR = PHANTOMJS_PDF_DIR
        self.PHANTOMJS_BIN = PHANTOMJS_BIN
        self.PHANTOMJS_GENERATE_PDF = PHANTOMJS_GENERATE_PDF
        self.KEEP_PDF_FILES = KEEP_PDF_FILES

        for attr in [
                'PHANTOMJS_COOKIE_DIR',
                'PHANTOMJS_PDF_DIR',
                'PHANTOMJS_BIN',
                'PHANTOMJS_GENERATE_PDF',
                'KEEP_PDF_FILES',
                'PHANTOMJS_ACCEPT_LANGUAGE',
                'PHANTOMJS_FORMAT',
                'PHANTOMJS_ORIENTATION',
                'PHANTOMJS_MARGIN',
                'PHANTOMJS_PAPER_SIZE',
                'PHANTOMJS_VIEWPORT_SIZE',
                'PHANTOMJS_COMPENSATE_FOR_V2_PDF_RENDERING_BUG']:
            if getattr(self, attr, None) is None:
                value = getattr(settings, attr, None)
                if value is None:
                    value = DEFAULT_SETTINGS[attr]
                setattr(self, attr, value)

        assert os.path.isfile(self.PHANTOMJS_BIN), \
            "%s doesnt exist, read the docs for more info." % self.PHANTOMJS_BIN
        for dir_ in [self.PHANTOMJS_COOKIE_DIR, self.PHANTOMJS_PDF_DIR]:
            if not os.path.isdir(dir_):
                os.makedirs(dir_)

    def _build_url(self, request):
        """Build the url for the request."""
        scheme, netloc, path, query, fragment = urlsplit(
            request.build_absolute_uri())
        protocol = scheme
        domain = netloc
        return '{protocol}://{domain}{path}'.format(
            protocol=protocol,
            domain=domain,
            path=path)

    def _set_source_file_name(self, basename=str(uuid.uuid1())):
        """Return the original source filename of the pdf."""
        return ''.join((os.path.join(self.PHANTOMJS_PDF_DIR, basename), '.pdf'))

    def _return_response(self, file_src, basename):
        """Read the generated pdf and return it in a django HttpResponse."""
        # Open the file created by PhantomJS
        return_file = None
        with open(file_src, 'rb') as f:
            return_file = f.readlines()

        response = HttpResponse(
            return_file,
            content_type='application/pdf'
        )
        content_disposition = 'attachment; filename=%s.pdf' % (basename)
        response['Content-Disposition'] = content_disposition

        if not self.KEEP_PDF_FILES:  # remove generated pdf files
            os.remove(file_src)

        return response

    def request_to_pdf(self, request, basename,
                       format=None,
                       orientation=None,
                       margin=None,
                       paper_size=None,
                       viewport_size=None,
                       compensate_for_v2_pdf_rendering_bug=None,
                       make_response=True,
                       url=None):
        """Receive request, basename and return a PDF in an HttpResponse.
            If `make_response` is True return an HttpResponse otherwise file_src. """

        format = format or self.PHANTOMJS_FORMAT
        orientation = orientation or self.PHANTOMJS_ORIENTATION
        margin = margin or self.PHANTOMJS_MARGIN
        paper_size = paper_size or self.PHANTOMJS_PAPER_SIZE or {
            "format": format,
            "orientation": orientation,
            "margin": margin
        }

        viewport_size = viewport_size or self.PHANTOMJS_VIEWPORT_SIZE
        compensate_for_v2_pdf_rendering_bug = (
            compensate_for_v2_pdf_rendering_bug or self.PHANTOMJS_COMPENSATE_FOR_V2_PDF_RENDERING_BUG
        )
        if compensate_for_v2_pdf_rendering_bug is None:
            compensate_for_v2_pdf_rendering_bug = 0

        file_src = self._set_source_file_name(basename=basename)
        try:
            os.remove(file_src)
            logger.info("Removed already existing file: %s", file_src)
        except OSError:
            pass

        if not url:
            url = self._build_url(request)

            domain = urlsplit(
                request.build_absolute_uri()
            ).netloc.split(':')[0]
        else:
            domain = urlsplit(url).netloc.split(':')[0]

        cookies = {
            domain: request.COOKIES
        }

        # Some servers have SSLv3 disabled, leave
        # phantomjs connect with others than SSLv3
        ssl_protocol = "--ssl-protocol=ANY"

        # PIPE hangs if the input is more than a couple
        # of pages (limit is 65k) so we use tmp files
        # - http://stackoverflow.com/questions/24979333/why-does-popen-hang-when-used-in-django-view/24979432#24979432
        # - https://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
        from tempfile import NamedTemporaryFile
        import sys
        try:
            phandle = Popen([
                self.PHANTOMJS_BIN,
                ssl_protocol,
                self.PHANTOMJS_GENERATE_PDF,
                url,
                file_src,
                json.dumps(cookies),
                self.PHANTOMJS_ACCEPT_LANGUAGE,
                json.dumps(paper_size),
                json.dumps(viewport_size),
                str(compensate_for_v2_pdf_rendering_bug)
            # ], close_fds=True, stdout=sys.stdout, stderr=sys.stderr)
            ], close_fds=True, stdout=NamedTemporaryFile(delete=True), stderr=NamedTemporaryFile(delete=True))
            phandle.communicate()

        finally:
            pass

        return self._return_response(file_src, basename) if make_response else file_src


def render_to_pdf(request, basename,
                  format=None,
                  orientation=None,
                  margin=None,
                  make_response=True,
                  url=None):
    """Helper function for rendering a request to pdf.
    Arguments:
        request = django request.
        basename = string to use for your pdf's filename.
        format = the page size to be applied; default if not given.
        orientation = the page orientation to use; default if not given.
        make_response = create or not an HttpResponse
    """
    request2pdf = RequestToPDF()
    response = request2pdf.request_to_pdf(request, basename, format=format,
                                          orientation=orientation, margin=margin, make_response=make_response, url=url)
    return response
