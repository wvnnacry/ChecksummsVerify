import os
import json
import zlib

print("СОЗДАНИЕ MANIFEST.JSON")
print("=" * 40)


files = ["file1.txt", "file2.txt", "file3.txt"]
manifest = {}


for filename in files:
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            crc = zlib.crc32(f.read()) & 0xFFFFFFFF
            manifest[filename] = f"0x{crc:08x}"
        print(f"✅ {filename}: 0x{crc:08x}")
    else:
        print(f"❌ {filename} не найден!")
        with open(filename, 'w') as f:
            f.write(f"Это тестовый файл {filename}")
        print(f"   Создан новый {filename}")
        with open(filename, 'rb') as f:
            crc = zlib.crc32(f.read()) & 0xFFFFFFFF
            manifest[filename] = f"0x{crc:08x}"
        print(f"   CRC для нового файла: 0x{crc:08x}")


with open("manifest.json", 'w') as f:
    json.dump(manifest, f, indent=2)

print("\n" + "=" * 40)
print(f"✅ manifest.json создан!")
print(f"Содержит {len(manifest)} файлов:")
for fname, crc in manifest.items():
    print(f"  {fname}: {crc}")