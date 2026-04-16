from bot.utils.attachments import AttachmentFactory


class AdminStatement:
    GET_GROUPS = """
        SELECT DISTINCT g.id, g.name
        FROM groups g
        JOIN results r ON g.id = r.group_id
        ORDER BY g.name
    """
    GET_TESTS = """
        SELECT DISTINCT t.id, t.name
        FROM tests t
        JOIN results r ON t.id = r.test_id
        WHERE r.group_id = $1
        ORDER BY t.name
    """
    GET_RESULTS = """
        SELECT DISTINCT ON (s.name, r.user_id) s.name, r.user_id, r.full_name, r.answers, r.points  
        FROM students s
        LEFT JOIN results r ON s.id = r.student_id AND r.test_id = $2
        WHERE s.group_id = $1
        ORDER BY s.name, r.user_id, r.points DESC, r.finished_at DESC
    """


class UserStatement:
    GET_GROUPS = "SELECT * FROM groups g ORDER BY g.name"
    GET_STUDENTS = "SELECT s.id, s.name FROM students s WHERE group_id = $1 ORDER BY s.name"
    GET_TESTS = "SELECT * FROM tests t ORDER BY t.name"
    GET_TASKS = """
        SELECT t.id, t.question, t.option1, t.option2, t.option3, t.option4
        FROM tasks t
        WHERE test_id = $1
        ORDER BY RANDOM()
        LIMIT 30
    """
    ADD_RESULT = """
        INSERT INTO results (
            user_id,               
            full_name,          
            group_id,       
            student_id,     
            test_id,
            answers,
            points,
            finished_at,
            duration
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)          
    """


def set_font(cls):
    for attribute, text in vars(cls).items():
        if not attribute.startswith("_"):
            setattr(cls, attribute, f"<code>{text}</code>")
    return cls


@set_font
class CommandText:
    STOP = "Выполнение прервано"


@set_font
class AdminText:
    SELECT_GROUP = "Шаг 1:\n\nВыберите группу"
    SELECT_TEST = "Шаг 2:\n\nВыберите тест"


@set_font
class UserText:
    SELECT_GROUP = "Шаг 1:\n\nВыберите вашу группу"
    SELECT_STUDENT = "Шаг 2:\n\nВыберите себя из списка"
    SELECT_TEST = "Шаг 3:\n\nВыберите необходимый тест"


class UserAttachment:
    CONFIRM = AttachmentFactory.from_items(("Начать тест", "Выбрать заново"))
    OPTIONS = AttachmentFactory.from_items(("1", "2", "3", "4"), 4)


PERMUTATIONS = (
    ("1", "2", "3", "4"),
    ("1", "2", "4", "3"),
    ("1", "3", "2", "4"),
    ("1", "3", "4", "2"),
    ("1", "4", "2", "3"),
    ("1", "4", "3", "2"),
    ("2", "1", "3", "4"),
    ("2", "1", "4", "3"),
    ("2", "3", "1", "4"),
    ("2", "3", "4", "1"),
    ("2", "4", "1", "3"),
    ("2", "4", "3", "1"),
    ("3", "1", "2", "4"),
    ("3", "1", "4", "2"),
    ("3", "2", "1", "4"),
    ("3", "2", "4", "1"),
    ("3", "4", "1", "2"),
    ("3", "4", "2", "1"),
    ("4", "1", "2", "3"),
    ("4", "1", "3", "2"),
    ("4", "2", "1", "3"),
    ("4", "2", "3", "1"),
    ("4", "3", "1", "2"),
    ("4", "3", "2", "1"),
)


PROGRESS_BARS = (
    "Вопрос 1 из 30:\n",
    "Вопрос 2 из 30:\n",
    "Вопрос 3 из 30:\n",
    "Вопрос 4 из 30:\n",
    "Вопрос 5 из 30:\n",
    "Вопрос 6 из 30:\n",
    "Вопрос 7 из 30:\n",
    "Вопрос 8 из 30:\n",
    "Вопрос 9 из 30:\n",
    "Вопрос 10 из 30:\n",
    "Вопрос 11 из 30:\n",
    "Вопрос 12 из 30:\n",
    "Вопрос 13 из 30:\n",
    "Вопрос 14 из 30:\n",
    "Вопрос 15 из 30:\n",
    "Вопрос 16 из 30:\n",
    "Вопрос 17 из 30:\n",
    "Вопрос 18 из 30:\n",
    "Вопрос 19 из 30:\n",
    "Вопрос 20 из 30:\n",
    "Вопрос 21 из 30:\n",
    "Вопрос 22 из 30:\n",
    "Вопрос 23 из 30:\n",
    "Вопрос 24 из 30:\n",
    "Вопрос 25 из 30:\n",
    "Вопрос 26 из 30:\n",
    "Вопрос 27 из 30:\n",
    "Вопрос 28 из 30:\n",
    "Вопрос 29 из 30:\n",
    "Вопрос 30 из 30:\n",
)
