import os
import random


def change_file(filename):
    """Просто меняет содержимое файла"""
    # Простые слова для заполнения
    words = ['кот', 'собака', 'дом', 'лес', 'река', 'море', 'гора', 'поле']

    # Случайный текст из 3-5 слов
    num_words = random.randint(3, 5)
    new_text = ' '.join(random.choices(words, k=num_words))

    # Записываем в файл
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_text)

    print(f"✅ {filename} -> {new_text}")


def change_all_files():
    """Меняет все .txt файлы"""
    print("\n=== ИЗМЕНЕНИЕ ФАЙЛОВ ===")

    # Находим все txt файлы
    files = [f for f in os.listdir('.') if f.endswith('.txt')]

    if not files:
        print("Нет txt файлов!")
        return

    for filename in files:
        change_file(filename)

    print("=" * 25)
    print("Готово! Запусти fix_manifest.py")


if __name__ == "__main__":
    change_all_files()