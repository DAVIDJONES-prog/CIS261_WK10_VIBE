#David Jones
#CIS261
#WK10 VIBE Coding - Student Grade Calculator

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections import Counter

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - non-Unix fallback
    termios = None
    tty = None


FILE_NAME = "student_grades.txt"
HEADERS = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]


MENU_PROMPT = "Select an option (1-5) or press ESC to exit: "
MENU_BORDER = "----------------------------------------"


def calculate_average(test1: float, test2: float, test3: float) -> float:
    return (test1 + test2 + test3) / 3


def calculate_grade(average: float) -> str:
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def build_student(name: str, student_id: str, test1: float, test2: float, test3: float) -> dict:
    average = calculate_average(test1, test2, test3)
    return {
        "name": name.strip(),
        "id": student_id.strip(),
        "test1": float(test1),
        "test2": float(test2),
        "test3": float(test3),
        "average": average,
        "grade": calculate_grade(average),
    }


def prompt_float(prompt: str) -> float:
    while True:
        value = input(prompt).strip()

        try:
            score = float(value)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if 0 <= score <= 100:
            return score

        print("Please enter a score between 0 and 100.")


def load_students(file_path: Path) -> list[dict]:
    students: list[dict] = []

    try:
        if not file_path.exists():
            return students

        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) != 7:
                    print(f"Skipping invalid record: {line}")
                    continue

                name, student_id, test1, test2, test3, _, _ = parts
                try:
                    students.append(
                        build_student(
                            name,
                            student_id,
                            float(test1),
                            float(test2),
                            float(test3),
                        )
                    )
                except ValueError:
                    print(f"Skipping invalid numeric data: {line}")
    except OSError as exc:
        print(f"Could not load records: {exc}")

    return students


def save_students(file_path: Path, students: list[dict]) -> None:
    try:
        with file_path.open("w", encoding="utf-8") as file:
            for student in students:
                file.write(
                    "|".join(
                        [
                            student["name"],
                            student["id"],
                            f"{student['test1']:.2f}",
                            f"{student['test2']:.2f}",
                            f"{student['test3']:.2f}",
                            f"{student['average']:.2f}",
                            student["grade"],
                        ]
                    )
                    + os.linesep
                )
    except OSError as exc:
        print(f"Could not save records: {exc}")


def format_row(columns: list[str], widths: list[int]) -> str:
    return " | ".join(column.ljust(width) for column, width in zip(columns, widths))


def display_students(students: list[dict]) -> None:
    if not students:
        print("No student records found.")
        return

    unique_students: list[dict] = []
    seen_names: set[str] = set()

    for student in students:
        normalized_name = student["name"].strip().lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)
        unique_students.append(student)

    rows = [
        [
            student["name"],
            student["id"],
            f"{student['test1']:.2f}",
            f"{student['test2']:.2f}",
            f"{student['test3']:.2f}",
            f"{student['average']:.2f}",
            student["grade"],
        ]
        for student in unique_students
    ]
    widths = [
        max(len(HEADERS[index]), max(len(row[index]) for row in rows))
        for index in range(len(HEADERS))
    ]

    print(format_row(HEADERS, widths))
    print(format_row(["-" * width for width in widths], widths))
    for row in rows:
        print(format_row(row, widths))
        print(f"Average: {row[5]} |   Grade: {row[6]}")


def display_statistics(students: list[dict]) -> None:
    if not students:
        print("No student records available for statistics.")
        return

    unique_students: list[dict] = []
    seen_names: set[str] = set()

    for student in students:
        normalized_name = student["name"].strip().lower()
        if normalized_name in seen_names:
            continue
        seen_names.add(normalized_name)
        unique_students.append(student)

    highest_student = max(unique_students, key=lambda s: s["average"])
    lowest_student = min(unique_students, key=lambda s: s["average"])
    class_average = sum(s["average"] for s in unique_students) / len(unique_students)


    print(
        f"Highest average: {highest_student['average']:.2f} ({highest_student['name']})"
    )
    print(
        f"Lowest average: {lowest_student['average']:.2f} ({lowest_student['name']})"
    )
    print(f"Class average: {class_average:.2f}")
    print()
    print("Grade Distribution:")

    grade_counts = Counter(student["grade"] for student in unique_students)
    for grade in ["A", "B", "C", "D", "F"]:
        count = grade_counts.get(grade, 0)
        if count:
            print(f"{grade}: {count} student(s)")


def search_student(students: list[dict]) -> None:
    print("Enter student name:")
    query = input().strip().lower()
    if not query:
        print("Search text cannot be empty.")
        return

    matches = [student for student in students if query in student["name"].lower()]

    if not matches:
        print("No matching student found.")
        return

    display_students(matches)


def add_student(students: list[dict]) -> None:
    while True:
        print("Enter student name:")
        name = input().strip()
        if not name:
            print("Student name cannot be empty.")
            continue

        student_id = input("Enter student ID: ").strip()
        if not student_id:
            print("Student ID cannot be empty.")
            continue

        test1 = prompt_float("Enter Test 1 score: ")
        test2 = prompt_float("Enter Test 2 score: ")
        test3 = prompt_float("Enter Test 3 score: ")

        student = build_student(name, student_id, test1, test2, test3)
        students.append(student)
        print(f"✓ Added Student: {name} ({student_id})")
        print(f"Average: {student['average']:.2f} |   Grade: {student['grade']}")

        another = input("Add another student? (y/n): ").strip().lower()
        if another != "y":
            break


def print_menu() -> None:
    print()
    print("Student Grade Calculator")
    print("1. Add new student record")
    print("2. Display all students")
    print("3. Search Students by Name")
    print("4. View Class Statistics")
    print("5. Save and Exit (or press ESC)")
    print(MENU_BORDER)


def get_menu_choice() -> str:
    print(MENU_BORDER)
    choice = input(MENU_PROMPT).strip()
    return "ESC" if choice.lower() in {"esc", "exit", "quit"} else choice


def main() -> None:
    file_path = Path(FILE_NAME)
    students = load_students(file_path)

    if students:
        print(f"Loaded {len(students)} student record(s) from {FILE_NAME}.")
    else:
        print("No existing student records loaded.")

    while True:
        print_menu()
        choice = get_menu_choice()

        if choice == "1":
            add_student(students)
            save_students(file_path, students)
        elif choice == "2":
            display_students(students)
        elif choice == "3":
            search_student(students)
        elif choice == "4":
            display_statistics(students)
        elif choice == "5":
            save_students(file_path, students)
            print("Records saved. Thank you for using Student Grade Calculator!")
            break
        elif choice == "ESC":
            save_students(file_path, students)
            print("Records saved. Thank you for using Student Grade Calculator!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, 5, or press ESC to exit.")


if __name__ == "__main__":
    main()

