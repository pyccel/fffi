import inspect
import os
import sys

LOG_WARN = True
LOG_DEBUG = False


if 'linux' in sys.platform:
    libext = '.so'
elif 'darwin' in sys.platform:
    libext = '.so'
elif 'win' in sys.platform:
    libext = '.dll'


def warn(output):
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, _, _) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('WARNING {}:{} {}():'.format(filename, line_number, function_name))
    print(output)


def debug(output):
    if not LOG_DEBUG:
        return
    caller_frame = inspect.currentframe().f_back
    (filename, line_number,
     function_name, _, _) = inspect.getframeinfo(caller_frame)
    filename = os.path.split(filename)[-1]
    print('')
    print('DEBUG {}:{} {}():'.format(filename, line_number, function_name))
    print(output)
