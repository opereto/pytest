from opereto.helpers.services import ServiceTemplate
from opereto.helpers.parsers import JunitToOperetoResults
from opereto.utils.validations import JsonSchemeValidator, validate_dict
from pyopereto.client import OperetoClient
import time, os, re

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)
        self.op_state = {}
        if os.path.exists(self.state_file):
            self.op_state = self._get_state()

    def validate_input(self):

        input_scheme = {
            "type": "object",
            "properties": {
                "parser_directory_path": {
                    "type": "string",
                    "minLength": 1
                },
                "listener_directory_path": {
                    "type": "string",
                    "minLength": 1
                },
                "results_xml_file": {
                    "type": "string",
                    "minLength": 1
                },
                "parser_frequency": {
                    "type": "integer",
                    "minValue": 1
                },
                "required": ['parser_frequency', 'results_xml_file', 'parser_directory_path', 'listener_directory_path'],
                "additionalProperties": True
            }
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

    def process(self):
        file_found=False
        self._print_step_title('Waiting for result directory..')
        rx = re.compile(self.input['results_xml_file'])
        sleep_interval=1
        while(True):
            if os.path.exists(self.input['parser_directory_path']):
                for file in os.listdir(self.input['parser_directory_path']):
                    if rx.match(file):
                        self.xunit_results_file = os.path.join(self.input['parser_directory_path'], file)
                        self.op_state['xunit_results_file']=self.xunit_results_file
                        self._save_state(self.op_state)
                        print('Results XML file found: {}'.format(self.xunit_results_file))
                        if self.debug_mode:
                            self._print_results_file(self.xunit_results_file)
                        file_found=True
                        break
            if file_found:
                break
            time.sleep(sleep_interval)
            if sleep_interval<10:
                sleep_interval+=1

        parser = JunitToOperetoResults(source_path=self.xunit_results_file, dest_path=self.input['listener_directory_path'])
        print('Start tracking for results modifications..')
        while(True):
            if os.path.exists(self.xunit_results_file):
                parser.parse(self.debug_mode)
            time.sleep(self.input['parser_frequency'])

        return self.client.SUCCESS

    def _print_results_file(self, file):
        with open(file, 'r') as result_file:
            print('Content of pytest results file: {}'.format(result_file.read()))

    def setup(self):
        self.xunit_results_file=None
        self.debug_mode = self.input['debug_mode']
        self._print_step_title('Start opereto pytest results parser..')

    def teardown(self):
        if 'xunit_results_file' in self.op_state:
            if os.path.exists(self.op_state['xunit_results_file']):
                self._print_results_file(self.op_state['xunit_results_file'])


if __name__ == "__main__":
    exit(ServiceRunner().run())
