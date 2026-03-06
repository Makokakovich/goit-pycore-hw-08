import pickle
from collections import UserDict
from datetime import datetime, date, timedelta
from typing import Callable


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        try:
            # перетворюємо рядок на об'єкт date з перевіркою формату
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: str, new_phone: str):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return
        raise ValueError("Phone not found.")

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        phones = ", ".join(p.value for p in self.phones)
        bd = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: phones: {phones}, birthday: {bd}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self) -> list:
        # повертає іменинників на наступні 7 днів з урахуванням вихідних
        today = date.today()
        result = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bd = record.birthday.value
            bd_this_year = bd.replace(year=today.year)
            if bd_this_year < today:
                bd_this_year = bd.replace(year=today.year + 1)
            delta = (bd_this_year - today).days
            if 0 <= delta <= 7:
                congrat_date = bd_this_year
                if congrat_date.weekday() == 5:
                    congrat_date += timedelta(days=2)
                elif congrat_date.weekday() == 6:
                    congrat_date += timedelta(days=1)
                result.append({
                    "name": record.name.value,
                    "congratulation_date": congrat_date.strftime("%d.%m.%Y"),
                })
        return result


def save_data(book: AddressBook, filename: str = "addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "addressbook.pkl") -> AddressBook:
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func: Callable) -> Callable:
    # декоратор для обробки помилок вводу
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Enter user name."
        except IndexError:
            return "Enter the argument for the command."
    return inner


def parse_input(user_input: str) -> tuple:
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:]
    return command, args


@input_error
def add_contact(args: list, book: AddressBook) -> str:
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args: list, book: AddressBook) -> str:
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list, book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    return ", ".join(p.value for p in record.phones)


@input_error
def add_birthday(args: list, book: AddressBook) -> str:
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: list, book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return "Birthday not set."
    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def birthdays(args: list, book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays next week."
    return "\n".join(f"{b['name']}: {b['congratulation_date']}" for b in upcoming)


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()

        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            if not book.data:
                print("No contacts saved.")
            else:
                for record in book.data.values():
                    print(record)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
