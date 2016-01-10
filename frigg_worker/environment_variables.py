import socket


def environment_variables_for_task(task):
    """
    This will build a dict with all the environment variables that
    should be present when running a build or deployment.

    :param task: A dict of the json payload with information about
                 the build task.
    :return: A dict of environment variables.
    """
    env = {
        'CI': 'frigg',
        'FRIGG': 'true',
        'FRIGG_CI': 'true',
        'GH_TOKEN': task['gh_token'],
        'FRIGG_BUILD_BRANCH': task['branch'],
        'FRIGG_BUILD_COMMIT_HASH': task['sha'],
        'FRIGG_BUILD_DIR': '~/builds/{0}'.format(task['id']),
        'FRIGG_BUILD_ID': task['id'],
        'FRIGG_DOCKER_IMAGE': task['image'],
        'FRIGG_WORKER': socket.getfqdn(),
    }

    if 'pull_request_id' in task:
        env['FRIGG_PULL_REQUEST_ID'] = task['pull_request_id']

    if 'build_number' in task:
        env['FRIGG_BUILD_NUMBER'] = task['build_number']

    if 'secrets' in task:
        env.update(task['secrets'])

    if 'environment_variables' in task:
        env.update(task['environment_variables'])

    return env

