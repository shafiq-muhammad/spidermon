import sys

from spidermon import settings

from .monitor import MonitorResult, monitors_step_required, actions_step_required


DOTS = {
    # Tests
    settings.MONITOR_STATUS_SUCCESS: '.',
    settings.MONITOR_STATUS_ERROR: 'E',
    settings.MONITOR_STATUS_FAILURE: 'F',
    settings.MONITOR_STATUS_SKIPPED: 's',
    settings.MONITOR_STATUS_EXPECTED_FAILURE: 'x',
    settings.MONITOR_STATUS_UNEXPECTED_SUCCESS: 'u',

    # Actions
    settings.ACTION_STATUS_SUCCESS: '.',
    settings.ACTION_STATUS_ERROR: 'E',
    settings.ACTION_STATUS_SKIPPED: 's',
}


class TextMonitorResult(MonitorResult):

    SEPARATOR_BOLD = '='
    SEPARATOR_LIGHT = '-'
    LINE_LENGTH = 70

    def __init__(self, stream=sys.stderr, verbosity=1):
        super(TextMonitorResult, self).__init__()
        self.stream = stream
        self.show_all = verbosity > 1
        self.use_dots = verbosity == 1

    def next_step(self):
        super(TextMonitorResult, self).next_step()
        self.write_title(self.step.name)

    def finish_step(self):
        super(TextMonitorResult, self).finish_step()
        if self.use_dots:
            self.write_line()
        if not self.step.successful:
            self.write_errors()
        self.write_run_footer()
        self.write_step_summary()

    @monitors_step_required
    def startTest(self, test):
        super(TextMonitorResult, self).startTest(test)
        self.write_run_start(test)

    @monitors_step_required
    def addSuccess(self, test):
        super(TextMonitorResult, self).addSuccess(test)
        self.write_run_result(test)

    @monitors_step_required
    def addError(self, test, error):
        super(TextMonitorResult, self).addError(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addFailure(self, test, error):
        super(TextMonitorResult, self).addFailure(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addSkip(self, test, reason):
        super(TextMonitorResult, self).addSkip(test, reason)
        self.write_run_result(test, reason)

    @monitors_step_required
    def addExpectedFailure(self, test, error):
        super(TextMonitorResult, self).addExpectedFailure(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test):
        super(TextMonitorResult, self).addUnexpectedSuccess(test)
        self.write_run_result(test)

    @actions_step_required
    def start_action(self, action):
        super(TextMonitorResult, self).start_action(action)
        self.write_run_start(action)

    @actions_step_required
    def add_action_success(self, action):
        super(TextMonitorResult, self).add_action_success(action)
        self.write_run_result(action)

    @actions_step_required
    def add_action_skip(self, action, reason):
        super(TextMonitorResult, self).add_action_skip(action, reason)
        self.write_run_result(action, reason)

    @actions_step_required
    def add_action_error(self, action, error):
        super(TextMonitorResult, self).add_action_error(action, error)
        self.write_run_result(action)

    def write(self, text):
        self.stream.write(text)

    def write_flush(self):
        self.stream.flush()

    def write_line_light(self):
        self.write_line(self.SEPARATOR_LIGHT*self.LINE_LENGTH)

    def write_line_bold(self):
        self.write_line(self.SEPARATOR_BOLD*self.LINE_LENGTH)

    def write_title(self, title):
        self.write_line(self._line_title(title))

    def write_line(self, text=None):
        self.write('%s\n' % (text or ''))

    def write_run_status(self, text, extra=None):
        self.write_line('%s%s' % (text, ' (%s)' % extra if extra else ''))

    def write_run_start(self, item):
        if self.show_all:
            self.write(item.name)
            self.write(" ... ")
            self.write_flush()

    def write_run_result(self, item, extra=None):
        if self.show_all:
            self.write_run_status(self.step[item].status, extra)
        elif self.use_dots:
            self.write(DOTS[self.step.results[item]])
            self.write_flush()

    def write_run_footer(self):
        self.write_line_light()
        self.write_line("{count:d} {item_name}{plural_suffix} in {time:.3f}s".format(
            count=self.step.number_of_items,
            item_name=self.step.item_result_class.name,
            plural_suffix='' if self.step.number_of_items == 1 else 's',
            time=self.step.time_taken,
        ))
        self.write_line()

    def write_errors(self):
        self.write_line()
        for status in self.step.error_statuses:
            for item in self.step.items_for_status(status):
                self.write_line_bold()
                self.write_line('%s: %s' % (item.status, item.name))
                self.write_line_light()
                self.write_line(item.error)
                self.write_line()

    def write_step_summary(self):
        self.write('OK' if self.step.successful else 'FAILED')
        infos = self.step.get_infos()
        if infos and sum(infos.values()):
            self.write_line(' (%s)' % ', '.join(['%s=%s' % (k, v) for k, v in infos.items() if v]))
        else:
            self.write_line()
        self.write_line()

    def _line_title(self, title, length=70, char=None):
        title_length = len(title)+2
        left_length = (length-title_length)/2
        right_length = left_length + length - title_length - left_length * 2
        char = char or self.SEPARATOR_LIGHT
        return '%s %s %s' % (char*left_length, title, char*right_length)
