import threading


try:
    # python2.7
    from Queue import Queue
except:
    # python3
    from queue import Queue


class ThreadedWorkerQueue:
    """
    queue that can be processed by multiple worker threads,
    calling the process_func on each item
    """
    def __init__(self, process_func, no_threads=2, auto_start_workers=True):
        self._q = Queue()
        self._process_func = process_func
        self._no_threads = no_threads
        self._threads = []
        self._is_worker_running = False
        self._lock = threading.Lock()

        if auto_start_workers is True:
            # automatically start the workers
            self.start_workers()

    def is_worker_running(self):
        """
        returns True, if worker threads are running
        """
        return self._is_worker_running

    def start_workers(self):
        """
        start all worker threads
        """
        with self._lock:
            for _ in range(self._no_threads):
                # start a new thread in daemon mode
                self._threads.append(
                    threading.Thread(target=self._worker_process)
                )
                self._threads[-1].daemon = True
                self._threads[-1].start()

            self._is_worker_running = True

    def stop_workers(self):
        """
        stop all worker threads
        """
        for _ in range(self._no_threads):
            self._q.put(None)
        for t in self._threads:
            t.join()
        self._is_worker_running = False

    def _worker_process(self):
        """
        called by each worker thread to process the item
        """
        while True:
            item = self._q.get()
            if item is None:
                break
            self._process_func(item)
            self._q.task_done()

    def put(self, item):
        """
        puts an item into the queue
        """
        self._q.put(item)

    def join(self, auto_stop_workers=True):
        """
        blocks until all items in the queue have been gotten and processed
        """
        self._q.join()

        if auto_stop_workers is True:
            self.stop_workers()
