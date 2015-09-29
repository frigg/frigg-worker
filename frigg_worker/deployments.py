import logging
import os

import yaml

from .jobs import Job, Result

logger = logging.getLogger(__name__)


class Deployment(Job):

    preset = None

    MAIN_TASKS_KEY = 'deploy_tasks'

    def run_deploy(self):
        task = None
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        self.load_preset()

        try:
            self.finished = False
            self.create_pending_tasks()
            self.start_services()
            self.report_run()

            for task in self.settings['setup_tasks']:
                self.run_setup_task(task)
                self.report_run()

            if self.preset:
                for task in self.preset['tasks']:
                    self.run_task(task)
                    self.report_run()

            for task in self.settings['preview']['tasks']:
                self.run_task(task)
                self.report_run()

            if self.preset:
                self.run_task(self.preset['daemon_task'])
                self.report_run()

        except Exception as e:
            self.error(task or '', e)
            logger.exception(e)
            logger.info('Build nr. {build.id} failed\n{0}'.format(str(e), build=self))
        finally:
            self.finished = True
            self.report_run()

            logger.info('Run of deploy {build.id} finished.'.format(build=self))

    def create_pending_tasks(self):
        """
        Creates pending task results in a dict on self.result with task string as key. It will also
        create a list on self.tasks that is used to make sure the serialization of the results
        creates a correctly ordered list.
        """
        for task in self.settings['setup_tasks']:
            self.setup_tasks.append(task)
            self.setup_results[task] = Result(task)

        if self.preset:
            for task in self.preset['tasks']:
                self.tasks.append(task)
                self.results[task] = Result(task)

        for task in self.settings['preview']['tasks']:
            self.tasks.append(task)
            self.results[task] = Result(task)

        if self.preset:
            self.tasks.append(self.preset['daemon_task'])
            self.results[self.preset['daemon_task']] = Result(self.preset['daemon_task'])

    def load_preset(self):
        """
        Loads preset if it is specified in the .frigg.yml
        """
        if 'preset' in self.settings['preview']:
            with open(os.path.join(os.path.dirname(__file__), 'presets.yaml')) as f:
                presets = yaml.load(f.read())

            if self.settings['preview']['preset'] in presets:
                self.preset = presets[self.settings['preview']['preset']]
            return self.preset
