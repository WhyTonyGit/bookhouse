import json
from pathlib import Path

DATA_FILE = Path("tasks.json")


def load_tasks():
    """Загрузка задач из файла."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Ошибка чтения файла, начинаю с пустого списка задач.")
        return []


def save_tasks(tasks):
    """Сохранение задач в файл."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except OSError:
        print("Не удалось сохранить задачи в файл.")


def show_menu():
    print("\n===== МЕНЮ ЗАДАЧ =====")
    print("1. Показать задачи")
    print("2. Добавить задачу")
    print("3. Отметить задачу как выполненную")
    print("4. Удалить задачу")
    print("5. Очистить выполненные задачи")
    print("0. Выход")


def show_tasks(tasks):
    if not tasks:
        print("Задач пока нет.")
        return

    print("\nВаши задачи:")
    for i, task in enumerate(tasks, start=1):
        status = "✓" if task["done"] else " "
        print(f"{i}. [{status}] {task['title']}")


def add_task(tasks):
    title = input("Введите текст задачи: ").strip()
    if not title:
        print("Пустая задача не добавлена.")
        return
    tasks.append({"title": title, "done": False})
    print("Задача добавлена.")


def mark_done(tasks):
    if not tasks:
        print("Нет задач для изменения.")
        return

    show_tasks(tasks)
    try:
        num = int(input("Номер задачи для отметки как выполненной: "))
        if 1 <= num <= len(tasks):
            tasks[num - 1]["done"] = True
            print("Задача отмечена как выполненная.")
        else:
            print("Нет задачи с таким номером.")
    except ValueError:
        print("Нужно ввести число.")


def delete_task(tasks):
    if not tasks:
        print("Нет задач для удаления.")
        return

    show_tasks(tasks)
    try:
        num = int(input("Номер задачи для удаления: "))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            print(f"Удалена задача: {removed['title']}")
        else:
            print("Нет задачи с таким номером.")
    except ValueError:
        print("Нужно ввести число.")


def clear_done(tasks):
    before = len(tasks)
    tasks[:] = [t for t in tasks if not t["done"]]
    removed = before - len(tasks)
    print(f"Удалено выполненных задач: {removed}")


def main():
    tasks = load_tasks()

    while True:
        show_menu()
        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
            save_tasks(tasks)
        elif choice == "3":
            mark_done(tasks)
            save_tasks(tasks)
        elif choice == "4":
            delete_task(tasks)
            save_tasks(tasks)
        elif choice == "5":
            clear_done(tasks)
            save_tasks(tasks)
        elif choice == "0":
            save_tasks(tasks)
            print("Выход из программы.")
            break
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()
