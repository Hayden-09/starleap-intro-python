

def time_since_epoch():
    import time
    seconds_per_day = 60 * 60 * 24
    seconds_per_hour = 60 * 60
    seconds_per_minute = 60

    t = time.time()
    print("t = ", t)
    days = int(t/seconds_per_day)
    print("days = ", days)
    remainder = t % (days * seconds_per_day)
    print("remainder = ", remainder)
    hours = int(remainder / seconds_per_hour)
    print("hours = ", hours)

time_since_epoch()