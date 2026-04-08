import pytest
import io
from PIL import Image

from utils.images import validate_image, resize_and_save_image, process_image_upload
from tests.factories.image import make_image_file, make_upload
from domain.core.errors import DomainValidationError, ConflictError, DomainError, NotFoundError


@pytest.mark.parametrize("image_format", ["PNG", "JPEG"])
def test_validate_image__valid_static_image__passes(image_format):
    file_obj = make_image_file(image_format)

    validate_image(file_obj)

    assert file_obj.tell() == 0


def test_validate_image__invalid_file__raises_domain_validation_error():
    file_obj = io.BytesIO(b"not-an-image")

    with pytest.raises(DomainValidationError):
        validate_image(file_obj)


def test_validate_image__animated_image__raises_domain_validation_error():
    file_obj = io.BytesIO()
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="blue")

    img1.save(file_obj, format="GIF", save_all=True, append_images=[img2])

    file_obj.seek(0)

    with pytest.raises(DomainValidationError):
        validate_image(file_obj)


def test_resize_and_save_image__valid_small_image__saves_file(tmp_path):
    file_obj = make_image_file()
    filename = "test.jpg"

    resize_and_save_image(file_obj, user_id=1, upload_folder=tmp_path, filename=filename)
    saved_file = tmp_path / filename

    assert saved_file.exists()
    assert saved_file.stat().st_size > 0


def test_resize_and_save_image__large_image__resizes(tmp_path):
    file_obj = make_image_file(format="JPEG", size=(3000, 2000))
    filename = "big.jpg"

    resize_and_save_image(file_obj, 1, tmp_path, filename, max_width=1000)

    with Image.open(tmp_path / filename) as saved:
        assert saved.width <= 1000
        assert saved.format in ["JPEG", "PNG"]


def test_resize_and_save_image__invalid_file__raises_domain_error(tmp_path):
    file_obj = io.BytesIO(b"not-an-image")

    with pytest.raises(DomainError):
        resize_and_save_image(file_obj, 1, tmp_path, "fail.jpg")


@pytest.mark.parametrize(
    "filename, mimetype, expected_exception",
    [
        ("image", None, DomainValidationError),
        ("image.jpg", "text/plain", DomainValidationError),
    ]
)
def test_process_image_upload__invalid_inputs__raises_error(tmp_path, filename, mimetype, expected_exception):
    upload = make_upload(filename=filename, mimetype=mimetype)

    with pytest.raises(expected_exception):
        process_image_upload(upload, user_id=1, upload_folder=tmp_path)


@pytest.mark.parametrize("filename", ["image.gif", "image.bmp", "image.tiff"])
def test_process_image_upload__unsupported_extension__raises_conflict_error(tmp_path, filename):
    upload = make_upload(filename=filename)

    with pytest.raises(ConflictError):
        process_image_upload(upload, 1, upload_folder=tmp_path)


def test_process_image_upload__valid_image__saves_file(tmp_path):
    upload = make_upload(filename="photo.png", mimetype="image/png")
    filename = process_image_upload(upload, user_id=1, upload_folder=tmp_path)

    saved = tmp_path / filename

    assert saved.exists()
    assert saved.stat().st_size > 0
    assert filename.endswith(".png") or filename.endswith(".jpg")


def test_process_image_upload__jpeg_extension__converts_to_jpg(tmp_path):
    upload = make_upload(filename="photo.jpeg", mimetype="image/jpeg")

    filename = process_image_upload(upload, user_id=1, upload_folder=tmp_path)

    assert filename.endswith(".jpg")

    saved = tmp_path / filename
    assert saved.exists()


def test_process_image_upload__missing_file_object__raises_not_found(tmp_path):
    upload = make_upload()
    # remove the file attribute to simulate missing object
    upload.file = None
    upload.stream = None

    with pytest.raises(NotFoundError):
        process_image_upload(upload, user_id=1, upload_folder=tmp_path)


def test_process_image_upload__animated_gif__raises_domain_validation_error(tmp_path):
    # Create animated GIF
    file_obj = io.BytesIO()
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="blue")

    img1.save(file_obj, format="GIF", save_all=True, append_images=[img2])

    file_obj.seek(0)

    upload = make_upload(filename="anim.jpg", mimetype="image/gif", file=file_obj)

    with pytest.raises(DomainValidationError):
        process_image_upload(upload, user_id=1, upload_folder=tmp_path)
