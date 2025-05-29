import mysql.connector
from datetime import datetime
from contextlib import contextmanager

class Counter:
    def __init__(self):
        self._count = 0
        self._is_open = False

    def __enter__(self):
        self._is_open = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_open = False
        if exc_type is not None:
            raise Exception("Ресурс не был закрыт правильно или произошла ошибка")

    def add(self):
        if not self._is_open:
            raise Exception("Работа с объектом счетчика не в ресурсном try")
        self._count += 1
        return self._count

    def get_count(self):
        return self._count

class Animal:
    def __init__(self, name, birth_date):
        self._name = name
        self._birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        self._commands = []

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        today = datetime.now().date()
        age = today.year - self._birth_date.year - ((today.month, today.day) < (self._birth_date.month, self._birth_date.day))
        return age

    @property
    def commands(self):
        return self._commands

    def add_command(self, command):
        self._commands.append(command)

    def __str__(self):
        return f"{self.__class__.__name__} {self._name}, возраст: {self.age} лет, команды: {', '.join(self._commands)}"

class Pet(Animal):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class PackAnimal(Animal):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Dog(Pet):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Cat(Pet):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Hamster(Pet):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Horse(PackAnimal):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Camel(PackAnimal):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class Donkey(PackAnimal):
    def __init__(self, name, birth_date):
        super().__init__(name, birth_date)

class AnimalRegistry:
    def __init__(self):
        self._animals = []
        self._db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Друзья_человека"
        )
        self._counter = Counter()

    def __del__(self):
        if self._db_connection.is_connected():
            self._db_connection.close()

    def add_animal(self, animal_type, name, birth_date, commands=None):
        try:
            with self._counter as c:
                if not all([animal_type, name, birth_date]):
                    raise ValueError("Все поля должны быть заполнены")
                
                animal_classes = {
                    "Собака": Dog,
                    "Кошка": Cat,
                    "Хомяк": Hamster,
                    "Лошадь": Horse,
                    "Верблюд": Camel,
                    "Осёл": Donkey
                }
                
                if animal_type not in animal_classes:
                    raise ValueError("Неизвестный тип животного")
                
                animal = animal_classes[animal_type](name, birth_date)
                
                if commands:
                    for command in commands.split(','):
                        animal.add_command(command.strip())
                
                self._animals.append(animal)
                
                # Добавление в базу данных
                cursor = self._db_connection.cursor()
                
                # Добавляем в таблицу Животные
                animal_type_category = 'Домашнее' if animal_type in ["Собака", "Кошка", "Хомяк"] else 'Вьючное'
                cursor.execute(
                    "INSERT INTO Животные (тип, имя, дата_рождения) VALUES (%s, %s, %s)",
                    (animal_type_category, name, birth_date)
                )
                animal_id = cursor.lastrowid
                
                # Добавляем в соответствующую таблицу
                if animal_type_category == 'Домашнее':
                    cursor.execute(
                        "INSERT INTO Домашние_животные (id, вид) VALUES (%s, %s)",
                        (animal_id, animal_type)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO Вьючные_животные (id, вид) VALUES (%s, %s)",
                        (animal_id, animal_type)
                    )
                
                # Добавляем команды
                if commands:
                    for command in commands.split(','):
                        cursor.execute(
                            "INSERT INTO Команды (животное_id, команда) VALUES (%s, %s)",
                            (animal_id, command.strip())
                        )
                
                self._db_connection.commit()
                cursor.close()
                
                c.add()
                print(f"Животное {name} успешно добавлено!")
                
        except Exception as e:
            print(f"Ошибка при добавлении животного: {e}")

    def list_animals(self):
        for animal in self._animals:
            print(animal)

    def teach_command(self, animal_name, command):
        for animal in self._animals:
            if animal.name == animal_name:
                animal.add_command(command)
                
                # Обновление в базе данных
                cursor = self._db_connection.cursor()
                cursor.execute(
                    "SELECT id FROM Животные WHERE имя = %s",
                    (animal_name,)
                )
                animal_id = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO Команды (животное_id, команда) VALUES (%s, %s)",
                    (animal_id, command)
                )
                self._db_connection.commit()
                cursor.close()
                
                print(f"Животное {animal_name} теперь умеет команду '{command}'")
                return
        print(f"Животное с именем {animal_name} не найдено")

    def show_commands(self, animal_name):
        for animal in self._animals:
            if animal.name == animal_name:
                print(f"Команды животного {animal_name}: {', '.join(animal.commands)}")
                return
        print(f"Животное с именем {animal_name} не найдено")

    def menu(self):
        while True:
            print("\nРеестр домашних животных")
            print("1. Завести новое животное")
            print("2. Список всех животных")
            print("3. Обучить животное новой команде")
            print("4. Показать команды животного")
            print("5. Выход")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                animal_type = input("Введите тип животного (Собака, Кошка, Хомяк, Лошадь, Верблюд, Осёл): ")
                name = input("Введите имя животного: ")
                birth_date = input("Введите дату рождения (ГГГГ-ММ-ДД): ")
                commands = input("Введите команды через запятую (необязательно): ")
                self.add_animal(animal_type, name, birth_date, commands)
            elif choice == "2":
                self.list_animals()
            elif choice == "3":
                name = input("Введите имя животного: ")
                command = input("Введите новую команду: ")
                self.teach_command(name, command)
            elif choice == "4":
                name = input("Введите имя животного: ")
                self.show_commands(name)
            elif choice == "5":
                break
            else:
                print("Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    registry = AnimalRegistry()
    registry.menu()