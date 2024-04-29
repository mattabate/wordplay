import fire


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


def seconds_to_time_len(seconds: int):
    "covert seconds to string like 1 hour 2 minutes 3 seconds eg"

    seconds_per_hour = 3600
    seconds_per_minute = 60

    hours = seconds // seconds_per_hour
    minutes = (seconds % seconds_per_hour) // seconds_per_minute
    seconds = seconds % seconds_per_minute

    time_string = ""
    if hours:
        time_string += f"{hours} hour{'s' if hours > 1 else ''} "
    if minutes:
        time_string += f"{minutes} minute{'s' if minutes > 1 else ''} "
    if seconds:
        time_string += f"{seconds} second{'s' if seconds > 1 else ''} "

    return time_string.strip()


def main(days: list[int] = [5, 2], verbose: bool = False):
    if len(days) != 2:
        raise ValueError("Please provide exactly two days")

    print(f"First passage \033[93m{days[0]}\033[0m days")
    print(f"First passage \033[93m{days[1]}\033[0m days")
    print("Ways to split:\n")

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

        print(f"\033[93mChunks: {i}\033[0m")
        for q in [0, 1]:
            print(f"Step size for Poem {q+1}:", seconds_to_time_len(int(steps[q])))
            if verbose:
                print("times", [seconds_to_time(tt) for tt in ll[q]])
        print()


if __name__ == "__main__":
    fire.Fire(main)
