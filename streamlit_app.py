from datetime import datetime
from itertools import chain

from requests import Session
from streamlit import json, set_page_config, sidebar


url_raw = "https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/"

with Session() as s1:
    catalog = s1.get(f"{url_raw}catalog.json").json()


def get_log() -> dict:
    with Session() as s2:
        return s2.get(f"{url_raw}log.json").json()


set_page_config(layout="wide")

log = get_log()
group = sidebar.selectbox("Учебная группа", log, index=None, placeholder="Надо выбрать")

if group:
    tn = sidebar.selectbox(
        "Название теста",
        {
            catalog[ti]
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
                if catalog[ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        ft, et, p = int(ft), int(et), int(p)
                        if p_max < p or p_max == p and et_min > et:
                            ft_, et_min, p_max, m_ = ft, et, p, m
            if ft_:
                if more:
                    ft_ = datetime.fromtimestamp(ft_).strftime("%H:%M %d.%m.%y")
                    et_min = f"{et_min // 60}:{et_min % 60:02}"
                    new[fn] = {f"{ft_} = {et_min} = {p_max} из 30": m_}
                else:
                    fn = " ".join([i for i in fn.split() if not i.isdigit()])
                    new[fn] = f"{p_max} из 30"
    else:
        for fn, ti_dict in log[group].items():
            for ti, r_list in ti_dict.items():
                if catalog[ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        ft, et = int(ft), int(et)
                        new.setdefault(fn, {})
                        ft = datetime.fromtimestamp(ft).strftime("%H:%M %d.%m.%y")
                        et = f"{et // 60}:{et % 60:02}"
                        new[fn][f"{ft} = {et} = {p} из 30"] = m
    json(new)
