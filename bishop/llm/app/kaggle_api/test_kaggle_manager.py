import pytest
from unittest.mock import patch, MagicMock

from pathlib import Path

from app.kaggle_api.manager import KaggleManager  # Исправленный импорт
from app.kaggle_api.exceptions import KaggleAuthenticationError, KaggleManagerError


@pytest.fixture
def kaggle_manager():
    return KaggleManager()


@pytest.fixture
def mock_api():
    with patch('app.kaggle_api.manager.KaggleApi') as mock:
        yield mock.return_value


def test_authenticate_success(kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    kaggle_manager.authenticate()
    mock_api.authenticate.assert_called_once()


def test_authenticate_failure(kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    mock_api.authenticate.side_effect = Exception("Auth error")

    with pytest.raises(KaggleAuthenticationError):
        kaggle_manager.authenticate()


def test_upload_dataset_success(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api

    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    (dataset_dir / "dummy.txt").write_text("some content")

    kaggle_manager.upload_dataset(dataset_dir)

    mock_api.dataset_create_version.assert_called_once_with(
        folder=dataset_dir,
        version_notes="A universal version of the dataset for launching training",
    )
    # Проверяем, что dataset-metadata.json был создан
    assert not (dataset_dir / "dataset-metadata.json").exists()


def test_upload_dataset_failure(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    mock_api.dataset_create_version.side_effect = Exception("Upload error")

    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    with pytest.raises(KaggleManagerError):
        kaggle_manager.upload_dataset(dataset_dir)


def test_run_script_success(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    mock_response = MagicMock()
    mock_response.ref = "some/ref"
    mock_api.kernels_push.return_value = mock_response

    script_path = tmp_path / "script.py"
    script_path.write_text("print('Hello')")

    ref = kaggle_manager.run_script(script_path)

    mock_api.kernels_push.assert_called_once()
    assert ref == "some/ref"
    # Проверяем, что kernel-metadata.json был удалён
    assert not (tmp_path / "kernel-metadata.json").exists()


def test_run_script_failure(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    mock_api.kernels_push.side_effect = Exception("Run error")

    script_path = tmp_path / "script.py"
    script_path.write_text("print('Hello')")

    with pytest.raises(KaggleManagerError):
        kaggle_manager.run_script(script_path)


def test_track_execution_complete(kaggle_manager, mock_api):
    kaggle_manager._api = mock_api

    mock_status = MagicMock()
    mock_status.status.name = "COMPLETE"
    mock_api.kernels_status.return_value = mock_status

    kaggle_manager.track_execution("some/ref")
    mock_api.kernels_status.assert_called_once_with("some/ref")


def test_track_execution_error(kaggle_manager, mock_api):
    kaggle_manager._api = mock_api

    mock_status = MagicMock()
    mock_status.status.name = "ERROR"
    mock_status.failure_message = "Some error occurred"
    mock_api.kernels_status.return_value = mock_status

    with pytest.raises(RuntimeError, match="failed with status: ERROR"):
        kaggle_manager.track_execution("some/ref")


def test_download_output_success(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api

    out_file_path = tmp_path / "output.txt"
    out_file_path.write_text("output data")

    mock_api.kernels_output.return_value = ([str(out_file_path)], "token")

    downloaded_files = kaggle_manager.download_output("some/ref", tmp_path)

    assert downloaded_files == [out_file_path]
    mock_api.kernels_output.assert_called_once_with(
        kernel="some/ref",
        path=tmp_path,
        force=True
    )


def test_download_output_no_output(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api

    mock_api.kernels_output.return_value = ([], "token")

    downloaded_files = kaggle_manager.download_output("some/ref", tmp_path)

    assert downloaded_files == []
    mock_api.kernels_output.assert_called_once()


def test_download_output_failure(tmp_path, kaggle_manager, mock_api):
    kaggle_manager._api = mock_api
    mock_api.kernels_output.side_effect = Exception("Download error")

    with pytest.raises(RuntimeError):
        kaggle_manager.download_output("some/ref", tmp_path)


def test_generate_py_script_config_success(tmp_path, kaggle_manager):
    script_path = tmp_path / "script.py"
    script_path.write_text("print('Hello')")

    kaggle_manager._KaggleManager__generate_py_script_config(script_path)

    metadata_file = tmp_path / "kernel-metadata.json"
    assert metadata_file.exists()

    with open(metadata_file) as f:
        content = f.read()
        assert "kernel_type" in content


def test_generate_py_script_config_invalid_path(kaggle_manager):
    with pytest.raises(ValueError):
        kaggle_manager._KaggleManager__generate_py_script_config(Path("/non/existent/script.py"))


def test_generate_dataset_config_success(tmp_path, kaggle_manager):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    dataset_metadata_file = kaggle_manager._generate_dataset_config(dataset_dir)

    assert dataset_metadata_file.exists()

    with open(dataset_metadata_file) as f:
        content = f.read()
        assert "licenses" in content


def test_generate_dataset_config_invalid_path(kaggle_manager):
    with pytest.raises(ValueError):
        kaggle_manager._generate_dataset_config(Path("/non/existent/folder"))
