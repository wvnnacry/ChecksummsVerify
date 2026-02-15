import os
import json
import zlib
import sys


def test_files():
    print("ПРОВЕРКА ФАЙЛОВ")
    print("=" * 50)


    if not os.path.exists("manifest.json"):
        print("❌ manifest.json не найден!")
        return False


    with open("manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f"✅ manifest.json загружен")
    print(f"Найдено файлов в манифесте: {len(manifest)}")


    for filename, crc in manifest.items():
        print(f"   {filename}: {crc}")

    print("\n" + "-" * 50)
    print("ПРОВЕРКА ФАЙЛОВ:")

    all_ok = True


    for filename, expected_crc in manifest.items():
        if not os.path.exists(filename):
            print(f"❌ Файл не найден: {filename}")
            all_ok = False
            continue


        with open(filename, 'rb') as f:
            actual_crc = zlib.crc32(f.read()) & 0xFFFFFFFF


        if isinstance(expected_crc, str):
            expected_crc = int(expected_crc, 16)


        if actual_crc == expected_crc:
            print(f"✅ {filename}: OK (0x{actual_crc:08x})")
        else:
            print(f"❌ {filename}: 0x{actual_crc:08x} != 0x{expected_crc:08x}")
            all_ok = False

    print("\n" + "=" * 50)
    if all_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        return True
    else:
        print("❌ ЕСТЬ ОШИБКИ!")
        return False


if __name__ == "__main__":
    sys.exit(0 if test_files() else 1)