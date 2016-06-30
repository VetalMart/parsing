from concurrent.futures import ThreadPoolExecutor, Future
import threading

def task_queue(task, iterator, concurrency=10, on_fail=lambda _: None):
    def submit():
        try:
            obj = next(iterator)
        except StopIteration:
            return
        if result.cancelled():
            return
        stats['delayed'] += 1
        future = executor.submit(task, obj)
        future.obj = obj
        future.add_done_callback(upload_done)
    def upload_done(future):
        with io_lock:
            submit()
            stats['delayed'] -= 1
            stats['done'] += 1
        if future.exception():
            on_fail(future.exception(), future.obj)
        if stats['delayed'] == 0:
            result.set_result(stats)

    def cleanup(_):
        with io_lock:
            executor.shutdown(wait=False)

    io_lock = threading.RLock()
    executor = ThreadPoolExecutor(concurrency)
    result = Future()
    result.stats = stats = {'done': 0, 'delayed': 0}
    result.add_done_callback(cleanup)

    with io_lock:
        for _ in range(concurrency):
            submit()

    return result
