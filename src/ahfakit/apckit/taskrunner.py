"""The threading safe unified execution.

Usage:
```
with TaskRunner() as tr:
    tr.emit(print, args=("Ln1: Hello World",))
    tr.put(lambda: print("Ln1: Hello World"))
```

```
tr = TaskRunner()
@tr.putter
def test():
    pass
test()
tr.close()
tr.join()
```
"""

from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import traceback
from types import MethodType
import typing as _t
import asyncio


def on_error(exc: Exception):
    print(
        "--------------------------------------------------\n"
        + "".join(traceback.format_exception(type(exc),
                                             exc, exc.__traceback__))
        + "\n--------------------------------------------------"
    )


class Task(object):
    """Basic task."""

    def __init__(self, target: _t.Optional[_t.Callable] = None, *,
                 args: _t.Iterable = (), kwds: _t.Optional[dict] = None):
        self.target = target
        self.args = args
        self.kwargs = kwds if kwds else {}
        self.result = None
        self.exc = None
        self.finished = threading.Event()

    def __call__(self):
        try:
            self.result = self.run()
        except Exception as exc:
            self.exc = exc
            on_error(exc)
        finally:
            self.finished.set()

    def run(self) -> _t.Any:
        if self.target is None:
            return None
        return self.target(*self.args, **self.kwargs)

    def wait(self, timeout: _t.Optional[float] = None):
        return self.finished.wait(timeout=timeout)

    def set_default(self, default):
        self.result = default

    @property
    def noerror(self):
        """Not error."""
        return self.exc is None


class TaskRunner(object):
    """Task execution center."""

    def __init__(self, que=queue.Queue, thr=threading.Thread):
        self.que = que()
        self.thr = thr(target=self.mainloop, daemon=True)
        self.started = False
        self.alive = threading.Event()
        self.ended = threading.Event()
        self.ended.set()

    def __enter__(self):
        if not self.started:
            self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.ended.wait()

    def run(self):
        while self.alive.is_set():
            task = self.que.get()
            if task is None:
                self.alive.clear()
                break
            task()

    def mainloop(self):
        self.run()
        self.ended.set()

    def start(self):
        """Start the threading."""
        self.started = True
        self.ended.clear()
        self.alive.set()
        self.thr.start()

    def close(self):
        """TaskRunner will closed after all task terminated."""
        self.que.put(None)

    def stop(self):
        """TaskRunner will closed after current task terminated."""
        self.alive.clear()
        self.close()

    def join(self):
        """Wait the TaskRunner terminated."""
        self.ended.wait()

    def put(self, func: _t.Callable[[], _t.Any]):
        """Put a callable to queue."""
        def wrapper():
            try:
                func()
            except Exception as exc:
                on_error(exc)

        self.que.put(wrapper)

    def putter(self, func: _t.Callable):
        """A decorator of `.put`."""
        return lambda *a, **kwa: self.put(lambda: func(*a, **kwa))

    def emit(self, func: _t.Callable, args: _t.Iterable = (), kwargs: _t.Optional[dict] = None, *, default=None, handler=Task):
        """Put a Task to queue."""
        task = handler(func, args=args, kwds=kwargs)
        if default is not None:
            task.result = default
        self.que.put(task)
        return task

    @_t.overload
    def emitter(self, *, default=None, handler=Task) -> _t.Callable[[_t.Callable], _t.Callable[..., Task]]:
        ...

    @_t.overload
    def emitter(self, func: _t.Callable, *, default=None, handler=Task) -> _t.Callable[..., Task]:
        ...

    def emitter(self, func=None, *, default=None, handler=Task) -> _t.Any:
        """A decorator of `.run`."""
        if func is None:
            return lambda f: self.emitter(f, default=default, handler=handler)
        return lambda *a, **kwa: self.emit(func, a, kwa, default=default, handler=handler)

    def proxy(self, default=None, handler=Task):
        def get_func(func: _t.Callable):
            def wrapper(*args, **kwargs):
                task = handler(func, args=args, kwds=kwargs)
                if default is not None:
                    task.result = default
                self.que.put(task)
                task.wait()
                return task.result
            return wrapper
        return get_func


class ThreadTaskRunner(TaskRunner):

    def __init__(self, que=queue.Queue, thr=threading.Thread):
        super().__init__(que, thr)
        self.thread_count = 4

    def run(self):
        with ThreadPoolExecutor(self.thread_count) as pool:
            while self.alive.is_set():
                task = self.que.get()
                if task is None:
                    self.alive.clear()
                    break
                pool.submit(task)
