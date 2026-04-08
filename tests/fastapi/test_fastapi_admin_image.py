import pytest
import io

from tests.fastapi.constants import ADMIN_ROUTES
from domain.core.errors import NotFoundError, DomainError
from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE

IMAGES_URL = "/api/admin/images"


def test_upload_image__staff_user__returns_201(
        authenticated_client,
        mocker,
):
    mock_process_image_upload = mocker.patch(
        f"{ADMIN_ROUTES}.process_image_upload",
        return_value="test_image.png"
    )
    client = authenticated_client(role=UserRole.staff)

    file = {"image": ("test.png", io.BytesIO(b"fake image data"), "image/png")}

    response = client.post(IMAGES_URL, files=file)
    mock_process_image_upload.assert_called_once()

    assert response.status_code == 201
    assert response.json() == {"filename": "test_image.png"}


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_upload_image__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.post(IMAGES_URL)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


@pytest.mark.parametrize("response_error, code, detail", [
    (DomainError("Invalid image"), 400, "Invalid image"),
    (NotFoundError("Image not found"), 404, "Image not found"),
])
def test_upload_image__service_errors__returns_400_or_404(
        authenticated_client,
        mocker,
        response_error,
        code,
        detail,
):
    mocker.patch(
        f"{ADMIN_ROUTES}.process_image_upload",
        side_effect=response_error
    )

    file = {"image": ("test.png", io.BytesIO(b"fake"), "image/png")}

    client = authenticated_client(role=UserRole.staff)

    response = client.post(IMAGES_URL, files=file)

    assert response.status_code == code
    assert response.json() == {"detail": detail}


def test_upload_image__no_file__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.post(IMAGES_URL)

    assert response.status_code == 422
