import logging
import os

from frigg_coverage import parse_coverage

from frigg_worker.errors import GitCloneError

from .jobs import Job

logger = logging.getLogger(__name__)


class Build(Job):

    def run_tests(self):
        task = None
        self.delete_working_dir()

        try:
            self.clone_repo()
        except GitCloneError as error:
            return self.handle_clone_error(error)

        try:
            self.finished = False
            self.create_pending_tasks()
            self.start_services()
            self.report_run()

            for task in self.settings.tasks['setup']:
                self.run_setup_task(task)
                self.report_run()

            for task in self.settings.tasks['tests']:
                self.run_task(task)
                self.report_run()

            if self.settings.has_after_tasks(self.succeeded):
                self.create_pending_after_task()
                self.report_run()
                for task in self.settings.tasks[self.after_tasks_key]:
                    self.run_after_task(task)
                    self.report_run()

            self.parse_coverage()

        except Exception as e:
            self.error(task or '', e)
            logger.exception(e)
            logger.info('Build nr. {build.id} failed\n{0}'.format(str(e), build=self))
        finally:
            self.delete_working_dir()
            self.finished = True
            self.report_run()

            logger.info('Run of build {build.id} finished.'.format(build=self))

    def parse_coverage(self):
        if self.settings.coverage:
            try:
                coverage_file = os.path.join(
                    self.working_directory,
                    self.settings.coverage['path']
                )
                self.coverage = parse_coverage(
                    self.docker.read_file(coverage_file),
                    self.settings.coverage['parser']
                )
            except Exception as e:
                logger.exception(e)
