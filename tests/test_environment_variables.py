import pytest
from frigg_worker.environment_variables import environment_variables_for_task


@pytest.fixture
def task():
    return {
        'id': 42,
        'gh_token': 'github',
        'branch': 'master',
        'sha': 'commit-hash',
        'image': 'frigg/frigg-test-base'
    }


@pytest.fixture
def task_with_secrets(task):
    fixture = {
        'secrets': {
            'PYPI_PASSWORD': 'a password',
        },
        'environment_variables': {
            'PYPI_USERNAME': 'frigg',
        }
    }
    fixture.update(task)
    return fixture


@pytest.fixture
def variables(task):
    return environment_variables_for_task(task)


@pytest.fixture
def variables_with_secrets(task_with_secrets):
    return environment_variables_for_task(task_with_secrets)


def test_should_add_ci_variables(variables):
    assert variables['CI'] == 'frigg'
    assert variables['FRIGG'] == 'true'
    assert variables['FRIGG_CI'] == 'true'


def test_should_add_gh_token(variables):
    assert variables['GH_TOKEN'] == 'github'


def test_should_add_branch(variables):
    assert variables['FRIGG_BUILD_BRANCH'] == 'master'


def test_should_add_hash(variables):
    assert variables['FRIGG_BUILD_COMMIT_HASH'] == 'commit-hash'


def test_should_add_dir(variables):
    assert variables['FRIGG_BUILD_DIR'] == '~/builds/42'


def test_should_build_id(variables):
    assert variables['FRIGG_BUILD_ID'] == 42


def test_should_docker_image(variables):
    assert variables['FRIGG_DOCKER_IMAGE'] == 'frigg/frigg-test-base'


def test_should_add_worker(mocker, task):
    mocker.patch(
        'socket.getfqdn',
        return_value='worker.frigg.io'
    )

    assert environment_variables_for_task(task)['FRIGG_WORKER'] == 'worker.frigg.io'


def test_should_add_pull_request_id(task):
    task_with_pull_request_id = {'pull_request_id': 42}
    task_with_pull_request_id.update(task)
    variables = environment_variables_for_task(task_with_pull_request_id)

    assert variables['FRIGG_PULL_REQUEST_ID'] == 42


def test_should_add_build_number(task):
    task_with_build_number = {'build_number': 42}
    task_with_build_number.update(task)
    variables = environment_variables_for_task(task_with_build_number)

    assert variables['FRIGG_BUILD_NUMBER'] == 42


def test_should_add_secrets(variables_with_secrets):
    assert variables_with_secrets['PYPI_PASSWORD'] == 'a password'


def test_should_add_environment_variables_from_task(variables_with_secrets):
    assert variables_with_secrets['PYPI_USERNAME'] == 'frigg'
