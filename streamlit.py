from itertools import chain

from streamlit import sidebar, json, set_page_config

from cache import get_log, login_data

log = get_log()

set_page_config(layout="wide")

group = sidebar.selectbox("Учебная группа", list(log), index=None)

if group:
    tn = sidebar.selectbox(
        "Название теста",
        {
            login_data["tests"][ti]
            for ti in chain.from_iterable(
                ti_dict.keys() for ti_dict in log[group].values()
            )
        },
        index=None,
    )

    best = sidebar.toggle("Только лучшие попытки")
    more = sidebar.toggle("Подробная информация")

    new = {}
    if best:
        for fn, ti_dict in log[group].items():
            p_max, et_min, k, v = 0, 0, None, None
            for ti, r_list in ti_dict.items():
                if login_data["tests"][ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        et, p = int(et), int(p)
                        if p_max < p or p_max == p and et_min > et:
                            p_max, et_min = p, et
                            if more:
                                k, v = (
                                    f"{fn} = {ft} = {et // 60}:{et % 60:02} = {p} из 30",
                                    m,
                                )
                            else:
                                fn = " ".join(
                                    [i for i in fn.split() if not i.isdigit()]
                                )
                                k, v = f"{fn} [{p}]", m
                if k:
                    new[k] = v
    else:
        for fn, ti_dict in log[group].items():
            for ti, r_list in ti_dict.items():
                if login_data["tests"][ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        et, p = int(et), int(p)
                        new.setdefault(fn, {})
                        if more:
                            new[fn][f"{ft} = {et // 60}:{et % 60:02} = {p} из 30"] = m
                        else:
                            new[fn][f"{p} из 30"] = m
    json(new)
