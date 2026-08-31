from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def mock_db():
    """Mock da sessão do banco de dados."""
    mock = MagicMock()
    mock.execute.return_value.scalar.return_value = 1
    mock.execute.return_value.fetchall.return_value = []
    mock.execute.return_value.fetchone.return_value = None
    mock.execute.return_value.mappings.return_value.fetchall.return_value = []
    mock.execute.return_value.mappings.return_value.fetchone.return_value = None
    return mock


@pytest.fixture
def mock_get_db(mock_db):
    """Mock do context manager get_db()."""
    with patch("database.connection.get_db") as mock:
        mock.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock.return_value.__exit__ = MagicMock(return_value=False)
        yield mock
