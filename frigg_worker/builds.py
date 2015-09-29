import logging
import os

from frigg_coverage import parse_coverage

from .jobs import Job

logger = logging.getLogger(__name__)


class Build(Job):

    def run_tests(self):
        task = None
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        try:
            self.finished = False
            self.create_pending_tasks()
            self.start_services()
            self.report_run()

            for task in self.settings['setup_tasks']:
                self.run_setup_task(task)
                self.report_run()

            for task in self.settings['tasks']:
                self.run_task(task)
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
        if 'coverage' in self.settings:
            try:
                coverage_file = os.path.join(
                    self.working_directory,
                    self.settings['coverage']['path']
                )
                self.coverage = parse_coverage(
                    self.docker.read_file(coverage_file),
                    self.settings['coverage']['parser']
                )
            except Exception as e:
                logger.exception(e)
