def seconds_to_time(seconds):
    # Constants for time calculations
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_MINUTE = 60

    # Calculate hours, minutes, and seconds
    hours = (
        seconds // SECONDS_PER_HOUR
    ) % 24  # Modulo 24 to wrap around if seconds > 86400 (more than one day)
    minutes = (seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    seconds = seconds % SECONDS_PER_MINUTE

    # Format AM or PM and adjust hours to 12-hour format
    period = "AM" if hours < 12 else "PM"
    hours = hours % 12
    if hours == 0:
        hours = 12  # Midnight or noon should be represented as 12

    # Create time string in HH:MM:SS format
    time_string = f"{hours:02}:{minutes:02}:{seconds:02} {period}"
    return time_string


if __name__ == "__main__":
    days = [5, 2]

    one_day = 24 * 60 * 60
    times = [float(one_day) * d for d in days]

    for i in range(1, 10000):
        steps = [t / i for t in times]
        if any([s % 1 != 0 for s in steps]):
            continue

        ll = [
            [l % one_day for l in range(0, int(times[q]), int(steps[q]))]
            for q in [0, 1]
        ]

        if ll[0] == ll[1]:
            continue

        if set(ll[0]) != set(ll[1]):
            continue

        print("number of chunks:", i)
        for q in [0, 1]:
            print(f"Passage {q+1}:", f"{days[q]} days")
            print("step size", steps[q])
            print("times", [seconds_to_time(tt) for tt in ll[q]])
        print()
