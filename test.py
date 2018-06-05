import schedule
import time

start_time = time.time()


def job():
    print("I'm working..." + str(time.time() - start_time))


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)