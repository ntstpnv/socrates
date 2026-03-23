from bisect import insort_left
from datetime import datetime
from itertools import chain

from bot.preloads import get_groups, get_results, get_students, get_tests
from requests import Session
from streamlit import cache_data, json, set_page_config, sidebar


@cache_data
def get_preloads(_session: Session):
    return get_groups(_session), get_students(_session), get_tests(_session)


with Session() as session:
    GROUPS, STUDENTS, TESTS = get_preloads(session)
    results = get_results(session)

set_page_config(layout="wide")

if latest := sidebar.toggle("Последние результаты", value=True):
    latest_r = [(0, "")] * 4
    for g_id, s_dict in results.items():
        for s, t_dict in s_dict.items():
            s_id, _, u_id = s.partition(" ")
            for t_id, r_list in t_dict.items():
                for r in r_list:
                    t, _, p, _ = r.split("=")
                    t = int(t)
                    if t > latest_r[0][0]:
                        r = f"{GROUPS[g_id]} {STUDENTS[s_id].name} {u_id} {TESTS[t_id]} {p} из 30"
                        insort_left(latest_r, (t, r))
                        del latest_r[0]

    json({datetime.fromtimestamp(t).strftime("%H:%M %d.%m.%y"): r for t, r in reversed(latest_r)})

elif group := sidebar.selectbox(
    "Учебная группа",
    sorted(GROUPS[g] for g in results.keys()),
    index=None,
    placeholder="Надо выбрать",
):
    g_id = next(k for k, v in GROUPS.items() if v == group)

    test = sidebar.selectbox(
        "Название теста",
        sorted(
            {
                TESTS[test]
                for test in chain.from_iterable(t_dict.keys() for t_dict in results[g_id].values())
            }
        ),
        index=None,
        placeholder="Надо выбрать",
    )

    new_r = {}
    if best := sidebar.toggle("Только лучшие попытки", value=True):
        for s, t_dict in results[g_id].items():
            s_id, _, u_id = s.partition(" ")
            t_, d_min, p_max = None, 0, 0
            for t_id, r_list in t_dict.items():
                if TESTS[t_id] == test:
                    for r in r_list:
                        t, d, p, _ = r.split("=")
                        t, d, p = int(t), int(d), int(p)
                        if p_max < p or p_max == p and d_min > d:
                            t_, d_min, p_max = t, d, p
            if t_:
                new_r[f"{STUDENTS[s_id].name} {u_id}"] = f"{p_max} из 30"
    else:
        for s, t_dict in results[g_id].items():
            s_id, _, u_id = s.partition(" ")
            s_ = f"{STUDENTS[s_id].name} {u_id}"
            for t_id, r_list in t_dict.items():
                if TESTS[t_id] == test:
                    for r in r_list:
                        t, d, p, m = r.split("=")
                        t, d = int(t), int(d)
                        t = datetime.fromtimestamp(t).strftime("%H:%M %d.%m.%y")
                        d = f"{d // 60:02}:{d % 60:02}"
                        new_r.setdefault(s_, {})
                        new_r[s_][f"{t} {d} {p} из 30"] = m

    new_r = dict(sorted(new_r.items()))
    json(new_r)
