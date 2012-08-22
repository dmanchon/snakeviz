import os
from collections import namedtuple

from . import pstatsloader
from . import handler
from . import upload


StatsRow = namedtuple('StatsRow', ['calls_value', 'calls_str',
                                   'tottime', 'tottime_str',
                                   'tottime_percall', 'tottime_percall_str',
                                   'cumtime', 'cumtime_str',
                                   'cumtime_percall', 'cumtime_percall_str',
                                   'file_line_func'])


def stats_rows(filename):
    time_fmt = '{0:>12.6g}'

    loader = pstatsloader.PStatsLoader(filename)

    rows = []

    for r in loader.rows.itervalues():
        if isinstance(r, pstatsloader.PStatRow):
            calls_value = r.recursive
            if r.recursive > r.calls:
                calls_str = '{0}/{1}'.format(r.recursive, r.calls)
            else:
                calls_str = str(r.calls)
            tottime = r.local
            tottime_str = time_fmt.format(tottime)
            tottime_percall = r.localPer
            tottime_percall_str = time_fmt.format(tottime_percall)
            cumtime = r.cummulative
            cumtime_str = time_fmt.format(cumtime)
            cumtime_percall = r.cummulativePer
            cumtime_percall_str = time_fmt.format(cumtime_percall)
            file_line_func = '{0}:{1}({2})'.format(r.filename,
                                                   r.lineno,
                                                   r.name)
            rows.append(StatsRow(calls_value, calls_str,
                                 tottime, tottime_str,
                                 tottime_percall, tottime_percall_str,
                                 cumtime, cumtime_str,
                                 cumtime_percall, cumtime_percall_str,
                                 file_line_func))

    return rows


class VizHandler(handler.Handler):
    def get(self, profile_name):
        if self.request.path.startswith('/viz/file/'):
            if self.settings['single_user_mode']:
                # Allow opening arbitrary files by full filesystem path
                # WARNING!!! Obviously this must be disabled by default
                # TODO: Some modicum of error handling here as well...
                if profile_name[0] != '/':
                    profile_name = '/' + profile_name
                filename = os.path.abspath(profile_name)
            else:
                # TODO: Raise a 404 error here
                pass
        else:
            filename = upload.storage_name(profile_name)

        rows = stats_rows(filename)
        rows.sort(key=lambda r: r.tottime, reverse=True)

        self.render('viz.html', profile_name=profile_name, stats_rows=rows)