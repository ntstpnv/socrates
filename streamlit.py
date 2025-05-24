from itertools import chain

from streamlit import sidebar, json, set_page_config

from git13 import get_log, login_data as ld

log = get_log()

set_page_config(layout="wide")

g = sidebar.selectbox(
    "Учебная группа", list(log), index=None, placeholder="Нужно выбрать"
)

tn_set = (
    {
        ld["tests"][ti]
        for ti in chain.from_iterable(ti_dict.keys() for ti_dict in log[g].values())
    }
    if g
    else None
)
tn = sidebar.selectbox("Название теста", tn_set, disabled=not g)

best = sidebar.toggle("Только лучшие попытки", disabled=not g)

ge = sidebar.number_input("Граница отображения", 0, 30, step=1, disabled=not g)

if g:
    if best:
        for fn, ti_dict in log[g].items():
            for ti, r_list in ti_dict.items():
                if ld["tests"][ti] == tn:
                    for r in r_list:
                        p_max, et_min, tmp = 0, 0, {}
                        ft, et, p, m = r.split("=")
                        et, p = int(et), int(p)
                        if p >= ge and (p_max < p or p_max == p and et_min > et):
                            p_max, et_min = p, et
                            tmp = {
                                "Студент": fn,
                                "Время завершения": ft,
                                "Длительность": f"{et // 60}:{et % 60:02}",
                                "Результат": f"{p} из 30",
                                "Ошибки": m,
                            }
                    else:
                        if tmp:
                            json(tmp)                
    else:
        new = {}
        for fn, ti_dict in log[g].items():
            for ti, r_list in ti_dict.items():
                if ld["tests"][ti] == tn:
                    for r in r_list:
                        ft, et, p, m = r.split("=")
                        et, p = int(et), int(p)
                        if p >= ge:
                            new.setdefault(fn, {})
                            new[fn][f"{ft} = {et // 60}:{et % 60:02} = {p} из 30"] = m
        json(new)
