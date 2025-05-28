from itertools import chain

from streamlit import json, set_page_config, sidebar

from cache import get_log, login_data


set_page_config(layout="wide")

log = get_log()
group = sidebar.selectbox("Учебная группа", log, index=None, placeholder="Надо выбрать")

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
        placeholder="Надо выбрать",
    )

    best = sidebar.toggle("Только лучшие попытки")
    more = sidebar.toggle("Подробная информация", disabled=not best)

    new = {}
    if best:
        for fn, ti_dict in log[group].items():
            ft_, et_min, p_max, m_ = None, 0, 0, None
            for ti, r_list in ti_dict.items():
                if login_data["tests"][ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        et, p = int(et), int(p)
                        if p_max < p or p_max == p and et_min > et:
                            ft_, et_min, p_max, m_ = ft, et, p, m
            if ft_:
                if more:
                    new.setdefault(fn, {})
                    new[fn] = {
                        f"{ft_} = {et_min // 60}:{et_min % 60:02} = {p_max} из 30": m_
                    }
                else:
                    new[" ".join([i for i in fn.split() if not i.isdigit()])] = (
                        f"{p_max} из 30"
                    )
    else:
        for fn, ti_dict in log[group].items():
            for ti, r_list in ti_dict.items():
                if login_data["tests"][ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        et = int(et)
                        new.setdefault(fn, {})
                        new[fn][f"{ft} = {et // 60}:{et % 60:02} = {p} из 30"] = m
    json(new)
