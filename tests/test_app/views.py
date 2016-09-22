from django.views.generic import TemplateView
from phantom_pdf import render_to_pdf

class IndexView(TemplateView):
    template_name="index.html"
    pdf_file_name="test"

    def get(self, request, *args, **kwargs):
        if self.request.GET.get("format") == "pdf":
            return render_to_pdf(request, self.pdf_file_name)
        return super(IndexView, self).get(request, *args, **kwargs)
