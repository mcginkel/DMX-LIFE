"""
Jinja2 template filters and custom functions
"""
import datetime
from jinja2 import nodes
from jinja2.ext import Extension

class NowExtension(Extension):
    """Jinja2 extension for getting the current time"""
    tags = {'now'}

    def __init__(self, environment):
        super(NowExtension, self).__init__(environment)
        environment.extend(
            now_functions={
                'year': lambda: datetime.datetime.now().year,
                'month': lambda: datetime.datetime.now().month,
                'day': lambda: datetime.datetime.now().day,
                'date': lambda: datetime.datetime.now().strftime('%Y-%m-%d'),
                'time': lambda: datetime.datetime.now().strftime('%H:%M:%S'),
                'datetime': lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        function = parser.stream.expect('name').value
        if function not in self.environment.now_functions:
            parser.fail('Unknown now function: %s' % function, lineno)
        call = self.environment.now_functions[function]()
        return nodes.Const(call).set_lineno(lineno)
