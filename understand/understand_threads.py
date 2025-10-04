import time

# -----------------------------
# Coroutines
# -----------------------------
def task1():
    print("Task 1 start")
    yield 2  # pretend "await sleep(2)"
    print("Task 1 end")

def task2():
    print("Task 2 start")
    yield 1  # pretend "await sleep(1)"
    print("Task 2 end")

# -----------------------------
# Minimal event loop
# -----------------------------
tasks = [
    (0, task1()),  # (time to run, coroutine)
    (0, task2())
]

while tasks:
    now = time.time()
    for i, (run_at, coro) in enumerate(tasks):
        if run_at <= now:
            try:
                delay = next(coro)  # run next step
                tasks[i] = (time.time() + delay, coro)  # reschedule
            except StopIteration:
                tasks[i] = None  # remove finished coroutine
    # remove finished tasks
    tasks = [t for t in tasks if t is not None]
    time.sleep(0.01)  # tiny sleep to avoid busy waiting
