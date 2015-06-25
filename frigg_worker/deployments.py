import logging

from .jobs import Job, Result

logger = logging.getLogger(__name__)


class Deployment(Job):

    MAIN_TASKS_KEY = 'deploy_tasks'

    def run_deploy(self):
        task = None
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        try:
            self.start_services()
            self.finished = False
            self.create_pending_tasks()
            self.report_run()

            for task in self.settings['setup_tasks']:
                self.run_setup_task(task)
                self.report_run()

            for task in self.settings['preview']['tasks']:
                self.run_task(task)
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

        for task in self.settings['preview']['tasks']:
            self.tasks.append(task)
            self.results[task] = Result(task)
