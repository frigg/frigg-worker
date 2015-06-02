import logging

from .jobs import Job

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

            for task in self.settings['deploy_tasks']:
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

