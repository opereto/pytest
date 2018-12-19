from opereto.helpers.services import ServiceTemplate
from opereto.helpers.parsers import JunitToOperetoResults
from opereto.utils.validations import JsonSchemeValidator, validate_dict
from pyopereto.client import OperetoClient
import time

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
                "required": ['parser_directory_path', 'listener_directory_path'],
                "additionalProperties": True
            }
        }

        validator = JsonSchemeValidator(self.input, input_scheme)
        validator.validate()

    def process(self):
        parser = JunitToOperetoResults(source_path=self.input['parser_directory_path'], dest_path=self.input['listener_directory_path'])
        while(True):
            parser.parse()
            if 'test_suite' in parser.tests:
                break
            time.sleep(20)

        self._print_step_title('Stopped opereto pytest results parser')
        print 'Results are ready at: {}'.format(self.input['listener_directory_path'])

        return self.client.SUCCESS

    def setup(self):
        pass

    def teardown(self):
        pass



if __name__ == "__main__":
    exit(ServiceRunner().run())
