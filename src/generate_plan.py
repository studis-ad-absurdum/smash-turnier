import random
from datetime import datetime, timedelta

def schedule_tournament(g, d, b, n, r, s, t_str):
    """
    g: group size (max)
    d: match duration (minutes)
    b: break & tick interval (minutes)
    n: total players
    r: number of rounds
    s: number of stations
    t_str: tournament start time "HH:MM"
    """
    # — Setup players and time deltas
    players   = [f"{i+1}" for i in range(n)]
    t0        = datetime.strptime(t_str, "%H:%M")
    match_dur = timedelta(minutes=d)
    break_dur = timedelta(minutes=b)

    # station availability, staggered by b
    station_next = [t0 + i*break_dur for i in range(s)]
    # each player ready at t0
    player_next  = {p: t0 for p in players}

    schedule = []  # will collect all matches

    # — Round loop
    for round_no in range(1, r+1):
        # 1) enforce round barrier: no round_i+1 until all done + break
        if round_no > 1:
            barrier = max(player_next.values())
        else:
            barrier = t0

        # 2) build this round's groups, avoiding any size-1 group
        random.shuffle(players)
        full = n // g
        rem  = n % g
        groups = []

        if rem == 1 and full >= 1:
            # take one full group + the 1 leftover => g+1 players
            # split into two groups sized floor((g+1)/2) and ceil((g+1)/2)
            big_chunk = players[: g+1 ]
            size1 = (g+1)//2
            size2 = (g+1) - size1
            groups.append(big_chunk[:size1])
            groups.append(big_chunk[size1:])
            used = g+1
            # the rest are full groups of size g
            for i in range(used, n, g):
                groups.append(players[i:i+g])
        else:
            # rem is 0 or >=2: just slice into g-sized, last one rem-sized (>=2 or 0)
            for i in range(0, n, g):
                groups.append(players[i:i+g])

        # pack into unscheduled list
        unscheduled = [{"round": round_no, "players": grp} for grp in groups]

        # 3) start ticking at later of earliest-station or barrier
        timeslot = max(min(station_next), barrier)

        # 4) schedule within this round, max 2 starts per tick
        while unscheduled:
            starts_this_tick = 0

            for st_idx in range(s):
                if starts_this_tick >= 2:
                    break
                if station_next[st_idx] <= timeslot:
                    # find a group whose players are all ready
                    for grp in list(unscheduled):
                        ready_time = max(player_next[p] for p in grp["players"])
                        if ready_time <= timeslot:
                            start = timeslot
                            end   = start + match_dur

                            schedule.append({
                                "round":   grp["round"],
                                "start":   start,
                                "end":     end,
                                "station": st_idx+1,
                                "players": grp["players"]
                            })

                            # update availability
                            station_next[st_idx] = end + break_dur
                            for p in grp["players"]:
                                player_next[p] = end + break_dur

                            unscheduled.remove(grp)
                            starts_this_tick += 1
                            break

            timeslot += break_dur

    # — Build Markdown output
    qual_start = t0
    qual_end   = max(m["end"] for m in schedule)
    md_lines = [
        "### Qualification Phase",
        f"- **Start:** {qual_start.strftime('%H:%M')}",
        f"- **Estimated End:** {qual_end.strftime('%H:%M')}",
        "",
        "| Match Start | Match End | Round | Station | Players |",
        "|-------------|-----------|-------|---------|---------|"
    ]
    for m in sorted(schedule, key=lambda x: x["start"]):
        player_list = ", ".join(m["players"])
        md_lines.append(
            f"| {m['start'].strftime('%H:%M')} "
            f"| {m['end'].strftime('%H:%M')} "
            f"| {m['round']} "
            f"| {m['station']} "
            f"| {player_list} |"
        )

    return "\n".join(md_lines)


if __name__ == "__main__":
    # Example parameters
    markdown = schedule_tournament(
        g=4,      # max group size
        d=6,      # match duration (min)
        b=2,      # break & tick interval (min)
        n=17,     # total players
        r=3,      # rounds
        s=3,      # stations
        t_str="09:00"
    )
    print(markdown)
