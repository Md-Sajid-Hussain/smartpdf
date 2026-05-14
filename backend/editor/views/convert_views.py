from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
import os

from ..utils.convert_utils import *

MEDIA_PATH = "media"


def save_file(file):
    path = os.path.join(MEDIA_PATH, file.name)
    with open(path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return path


@csrf_exempt
def pdf_to_word_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    output = pdf_to_word(path)
    return FileResponse(open(output, "rb"), as_attachment=True)


@csrf_exempt
def word_to_pdf_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    output = word_to_pdf(path)
    return FileResponse(open(output, "rb"), as_attachment=True)


@csrf_exempt
def pdf_to_image_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    outputs = pdf_to_images(path)
    return FileResponse(open(outputs[0], "rb"), as_attachment=True)


@csrf_exempt
def image_to_pdf_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    output = image_to_pdf(path)
    return FileResponse(open(output, "rb"), as_attachment=True)


@csrf_exempt
def ppt_to_pdf_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    output = ppt_to_pdf(path)
    return FileResponse(open(output, "rb"), as_attachment=True)


@csrf_exempt
def excel_to_pdf_api(request):
    file = request.FILES.get("file")
    path = save_file(file)
    output = excel_to_pdf(path)
    return FileResponse(open(output, "rb"), as_attachment=True)