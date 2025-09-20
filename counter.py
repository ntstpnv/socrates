from collections import Counter, defaultdict, namedtuple
from docx import Document
from re import search


file_name = input("Введите название фаила без расширения: ")
doc = Document(f"{file_name}.docx")

Cell = namedtuple("Cell", ["row", "column", "text"])
check, r_dict = [], defaultdict(list)

for table in doc.tables:
    c_list = [
        Cell(i, j, cell.text.replace("\n", "->"))
        for i, row in enumerate(table.rows, 1)
        for j, cell in enumerate(row.cells, 1)
    ]

    t_dict, g_list = defaultdict(dict), []
    for c_tuple in c_list:
        t_dict[c_tuple.row][c_tuple.column] = c_tuple.text[:10].ljust(10)
        if search(r"(?i)гр\. [оз]ф", c_tuple.text):
            g_list.append(c_tuple)

    check.append("\n".join([f"{str(i).zfill(2)}: {j}" for i, j in t_dict.items()]))

    for g_tuple in g_list:
        r_dict[g_tuple.text].extend(
            [
                f'"{c_tuple.text}"'
                for c_tuple in c_list
                if all(
                    [
                        c_tuple.column == g_tuple.column,
                        c_tuple.text.strip(),
                        c_tuple.text != g_tuple.text,
                    ]
                )
            ]
        )


with open(f"{file_name}.txt", "w", encoding="utf-8") as file:
    for group, r_list in r_dict.items():
        separator = "-" * len(group)
        file.write(f"{separator}\n{group}\n{separator}\n")
        for discipline, amount in sorted(Counter(r_list).items()):
            file.write(f"{discipline}: {amount}\n")
    separator = "-" * 19
    file.write(f"{separator}\nДанные для проверки\n{separator}\n")
    file.write("\n\n".join(check))