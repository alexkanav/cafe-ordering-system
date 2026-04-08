import io

from tests.flask.constants import ADMIN_ROUTES
from domain.core.errors import NotFoundError, DomainError
from utils.enums import UserRole

IMAGES_URL = "/api/admin/images"


def test_upload_image__staff_user__returns_201(
        authenticated_client,
        mocker,
):
    mock_process = mocker.patch(
        f"{ADMIN_ROUTES}.process_image_upload",
        return_value="test_image.png"
    )
    client = authenticated_client(role=UserRole.staff)

    data = {
        "image": (io.BytesIO(b"fake image data"), "test.png")
    }
    response = client.post(
        IMAGES_URL,
        data=data,
        content_type="multipart/form-data"
    )
    mock_process.assert_called_once()

    assert response.status_code == 201
    assert response.get_json() == {"filename": "test_image.png"}


def test_upload_image__client_user__returns_403(authenticated_client):
    client = authenticated_client(role=UserRole.client)

    response = client.post(IMAGES_URL)

    assert response.status_code == 403


def test_upload_image__unauthenticated__returns_401(api_client):
    response = api_client.post(IMAGES_URL)

    assert response.status_code == 401


def test_upload_image__domain_error__returns_400(
        authenticated_client,
        mocker
):
    mocker.patch(
        f"{ADMIN_ROUTES}.process_image_upload",
        side_effect=DomainError("Invalid image")
    )
    client = authenticated_client(role=UserRole.staff)

    data = {
        "image": (io.BytesIO(b"fake image data"), "test.png")
    }
    response = client.post(
        IMAGES_URL,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    assert response.get_json() == {"detail": "Invalid image"}


def test_upload_image__not_found_error__returns_404(
        authenticated_client,
        mocker
):
    mocker.patch(
        f"{ADMIN_ROUTES}.process_image_upload",
        side_effect=NotFoundError("User not found")
    )

    data = {
        "image": (io.BytesIO(b"fake image data"), "test.png")
    }

    client = authenticated_client(role=UserRole.staff)

    response = client.post(
        IMAGES_URL,
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 404
    assert response.get_json() == {"detail": "User not found"}
