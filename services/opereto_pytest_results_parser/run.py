from opereto.helpers.services import ServiceTemplate
from opereto.helpers.parsers import JunitToOperetoResults
from opereto.utils.validations import JsonSchemeValidator, validate_dict
from pyopereto.client import OperetoClient
import time, os, fnmatch

class ServiceRunner(ServiceTemplate):

    def __init__(self, **kwargs):
        self.client = OperetoClient()
        ServiceTemplate.__init__(self, **kwargs)
        self._print_step_title('Start opereto pytest results parser..')


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
        while(True):
            if os.path.exists(self.input['parser_directory_path']):
                for file in os.listdir(self.input['parser_directory_path']):
                    if fnmatch.fnmatch(file, self.input['results_xml_file']):
                        self.xunit_results_file = os.path.join(self.input['parser_directory_path'], file)
                        print 'Results XML file found: {}'.format(self.xunit_results_file)
                        file_found=True
                        break
            if file_found:
                break
            time.sleep(1)

        parser = JunitToOperetoResults(source_path=self.xunit_results_file, dest_path=self.input['listener_directory_path'])
        print 'Start tracking for results modifications..'
        while(True):
            if os.path.exists(self.xunit_results_file):
                parser.parse()
                if 'test_suite' in parser.tests:
                    break
            time.sleep(self.input['parser_frequency'])

        self._print_step_title('Stopped opereto pytest results parser')
        print 'Results are ready at: {}'.format(self.input['listener_directory_path'])

        return self.client.SUCCESS

    def setup(self):
        self.xunit_results_file=None


    def teardown(self):
        pass



if __name__ == "__main__":
    exit(ServiceRunner().run())
