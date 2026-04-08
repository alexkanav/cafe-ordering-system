import io
from PIL import Image


class FakeUpload:
    def __init__(self, file_obj, filename="image.png", mimetype="image/png"):
        self.file = file_obj
        self.filename = filename
        self.mimetype = mimetype


def make_image_file(format="PNG", size=(100, 100)):
    file = io.BytesIO()
    img = Image.new("RGB", size, color="red")
    img.save(file, format=format)
    file.seek(0)
    return file


def make_upload(format="PNG", filename="image.png", mimetype="image/png", file=None):
    if file is None:
        file = make_image_file(format)
    return FakeUpload(file, filename, mimetype)
