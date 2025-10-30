import pytest

pytest_plugins = ["tests.plugins.setup_plugin"]


@pytest.fixture(autouse=True)
def auto_setup(setup_env_variables, authorized):  # pylint: disable=unused-argument
    yield
