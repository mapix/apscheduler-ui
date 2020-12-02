
import traceback
import sys
import logging
from io import StringIO
from contextlib import contextmanager
from functools import wraps


__all__ = ['patch_scheduler']

LAST_JOB_RUN_DETAIL_INFOS = {}


class Context(object):

    def __init__(self, name):
        logger = logging.getLogger('jobs.%s' % name)
        logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        log_handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(levelname)s: %(message)s")
        log_handler.setFormatter(fmt)
        logger.handlers = []
        logger.addHandler(log_handler)
        self.logger = logger
        self.log_handler = log_handler
        self.info = {}

    @contextmanager
    def log_buffer(self):
        with StringIO() as buffer:
            original_stream = self.log_handler.stream
            self.log_handler.stream = buffer
            try:
                yield buffer
            finally:
                self.log_handler.stream = original_stream


class ContextWrapper(object):

    def __init__(self):
        self.context = None

    def set_context(self, context):
        self.context = context

    @property
    def info(self):
        return self.context.info

    @property
    def logger(self):
        return self.context.logger


def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    exception_str = exception_str[:-1]
    return exception_str


def patch_scheduler(scheduler):
    if getattr(scheduler, '_apischedulerui_patched', None):
        return

    setattr(scheduler, '_apischedulerui_patched', True)
    origin_add_job = scheduler.add_job

    def _patched_add_job(func, *args, **kwargs):
        job_id = None
        context_wrapper = ContextWrapper()

        @wraps(func)
        def _(*args, **kwargs):
            context = Context(job_id)
            context_wrapper.set_context(context)
            global LAST_JOB_RUN_DETAIL_INFOS
            with context.log_buffer() as buffer:
                buffer.truncate(0)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context.logger.error(format_exception(e))
                    raise
                finally:
                    LAST_JOB_RUN_DETAIL_INFOS[job_id] = (context.info, buffer.getvalue())

        if len(args) >= 3:
            fkw = args[2] or {}
            fkw['context'] = context_wrapper
            args = list(args)
            args[2] = fkw
            args = tuple(args)
        else:
            kwargs['args'] = tuple([context_wrapper] + list(kwargs.get('args') or []))

        if len(args) >= 4:
            args = list(args)
            args[3] = args[3] or (func.__qualname__ if callable(func) else func)
            args = tuple(args)
        else:
            kwargs['id'] = kwargs.get('id', None) or (func.__qualname__ if callable(func) else func)
        job = origin_add_job(_, *args, **kwargs)
        job_id = job.id
        return job
    scheduler.add_job = _patched_add_job
