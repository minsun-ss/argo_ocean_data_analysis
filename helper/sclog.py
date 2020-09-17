import sys
import traceback
import logging

def logging_to_file(filename):
    logging.basicConfig(filename=filename, filemode='w', level=logging.DEBUG,
                        format = '%(asctimes)s - %(levelname)s - %(message)s')

def get_function_name():
    stack = traceback.extract_tb(sys.exc_info()[2], 1)
    return stack[0][3]

def log_exception(e):
    error_message = f'Function {get_function_name()} raised {e.__class__} ({e.__doc__})'
    print(error_message)
    logging.error(f'Function {get_function_name()} raised {e.__class__} ({e.__doc__})')