import random
from datetime import datetime, timedelta

def schedule_tournament(g, d, b, n, r, s, t_str):
    """
    g: max group size
    d: match duration (minutes)
    b: break & tick interval (minutes)
    n: total players
    r: rounds
    s: stations
    t_str: start time "HH:MM"
    """
    # — Setup
    players   = [f"{i+1}" for i in range(n)]
    t0        = datetime.strptime(t_str, "%H:%M")
    match_dur = timedelta(minutes=d)
    break_dur = timedelta(minutes=b)

    # initial station availability: pair them so two stations are free each tick
    station_next = [t0 + (i//2)*break_dur for i in range(s)]
    player_next  = {p: t0 for p in players}

    schedule = []

    for round_no in range(1, r+1):
        # barrier: no round_i+1 until all players done round_i + break
        barrier = max(player_next.values()) if round_no > 1 else t0

        # build groups, avoiding any size‑1
        random.shuffle(players)
        full = n // g
        rem  = n % g
        groups = []

        if rem == 1 and full >= 1:
            chunk = players[:g+1]
            size1 = (g+1)//2
            groups.append(chunk[:size1])
            groups.append(chunk[size1:])
            used = g+1
            for i in range(used, n, g):
                groups.append(players[i:i+g])
        else:
            for i in range(0, n, g):
                groups.append(players[i:i+g])

        unscheduled = [{"round": round_no, "players": grp} for grp in groups]

        # start ticking at the later of earliest‑free station or barrier
        timeslot = max(min(station_next), barrier)

        while unscheduled:
            starts_this_tick = 0

            for st_idx in range(s):
                if starts_this_tick >= 2:
                    break
                if station_next[st_idx] <= timeslot:
                    for grp in list(unscheduled):
                        if max(player_next[p] for p in grp["players"]) <= timeslot:
                            start = timeslot
                            end   = start + match_dur

                            schedule.append({
                                "round":   grp["round"],
                                "start":   start,
                                "end":     end,
                                "station": st_idx+1,
                                "players": grp["players"]
                            })

                            station_next[st_idx] = end + break_dur
                            for p in grp["players"]:
                                player_next[p] = end + break_dur

                            unscheduled.remove(grp)
                            starts_this_tick += 1
                            break

            timeslot += break_dur

    # — Markdown output
    qual_start = t0
    qual_end   = max(m["end"] for m in schedule)
    md = [
        "### Qualification Phase",
        f"- **Start:** {qual_start.strftime('%H:%M')}",
        f"- **Estimated End:** {qual_end.strftime('%H:%M')}",
        "",
        "| Match Start | Match End | Round | Station | Players |",
        "|-------------|-----------|-------|---------|---------|"
    ]
    for m in sorted(schedule, key=lambda x: x["start"]):
        md.append(
            f"| {m['start'].strftime('%H:%M')} "
            f"| {m['end'].strftime('%H:%M')} "
            f"| {m['round']} "
            f"| {m['station']} "
            f"| {', '.join(m['players'])} |"
        )

    return "\n".join(md)