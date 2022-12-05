import logging
from configparser import RawConfigParser, NoSectionError

def log_wrapper(original_function):
    '''
    Wraps a function to log its execution. Logs are sent to 'logger' in kwargs. Otherwise, the root logger is used.
    '''
    def wrapper_function(*args, **kwargs):
        try:
            result = original_function(*args, **kwargs)
            return result
        except Exception as e:
            kwargs.get("logger", logging).exception(f"Failed to execute {original_function.__name__} - {e}")
    return wrapper_function


class RawConfigParser(RawConfigParser):
    def options(self, section, no_defaults=False, **kwargs):
        if no_defaults:
            try:
                return list(self._sections[section].keys())
            except KeyError:
                raise NoSectionError(section)
        else:
            return super().options(section, **kwargs)