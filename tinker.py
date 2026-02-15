import json
import xml.etree.ElementTree as ET
import hashlib
import os
import sys
import zlib
import argparse
from pathlib import Path
from abc import ABC, abstractmethod


class ManifestParser(ABC):
    @abstractmethod
    def parse(self, filepath):
        pass


class ChecksumCalculator(ABC):
    @abstractmethod
    def calculate(self, filepath):
        pass

    @abstractmethod
    def get_type(self):
        pass



class JsonManifestParser(ManifestParser):
    def parse(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        files_to_check = []

        if isinstance(data, dict):
            if 'files' in data:
                for file_info in data['files']:
                    files_to_check.append({
                        'filename': file_info['filename'],
                        'expected': file_info.get('checksum') or file_info.get('crc32') or file_info.get('hash'),
                        'type': file_info.get('type', 'crc32').lower()
                    })
            else:
                for filename, checksum in data.items():
                    if isinstance(checksum, dict):
                        files_to_check.append({
                            'filename': filename,
                            'expected': checksum.get('checksum') or checksum.get('crc32') or checksum.get('hash'),
                            'type': checksum.get('type', 'crc32').lower()
                        })
                    else:
                        files_to_check.append({
                            'filename': filename,
                            'expected': str(checksum),
                            'type': 'crc32'
                        })
        elif isinstance(data, list):
            for file_info in data:
                files_to_check.append({
                    'filename': file_info['filename'],
                    'expected': file_info.get('checksum') or file_info.get('crc32') or file_info.get('hash'),
                    'type': file_info.get('type', 'crc32').lower()
                })

        return files_to_check


class XmlManifestParser(ManifestParser):
    def parse(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        files_to_check = []

        for elem in root.findall('.//file') or root.findall('.//checksum'):
            filename = elem.get('name') or elem.get('filename') or elem.get('path')
            if not filename:
                continue

            checksum = elem.get('checksum') or elem.get('crc32') or elem.get('hash') or elem.text
            checksum_type = elem.get('type', 'crc32').lower()

            files_to_check.append({
                'filename': filename,
                'expected': checksum,
                'type': checksum_type
            })

        return files_to_check



class Crc32Calculator(ChecksumCalculator):
    def calculate(self, filepath):
        with open(filepath, 'rb') as f:
            return zlib.crc32(f.read()) & 0xFFFFFFFF

    def get_type(self):
        return 'crc32'


class Md5Calculator(ChecksumCalculator):
    def calculate(self, filepath):
        try:
            return hashlib.md5(open(filepath, "rb").read()).hexdigest()
        except:
            return None

    def get_type(self):
        return 'md5'


class Sha256Calculator(ChecksumCalculator):
    def calculate(self, filepath):
        try:
            with open(filepath, "rb") as file:
                data = file.read()
            return hashlib.sha256(data).hexdigest()
        except:
            return None

    def get_type(self):
        return 'sha256'


class ChecksumCalculatorFactory:
    _calculators = {
        'crc32': Crc32Calculator(),
        'md5': Md5Calculator(),
        'sha256': Sha256Calculator()
    }

    @classmethod
    def get_calculator(cls, checksum_type):
        return cls._calculators.get(checksum_type.lower())



def calculate_crc32(filepath):
    calculator = Crc32Calculator()
    result = calculator.calculate(filepath)
    return result


def calculate_md5(filepath):
    calculator = Md5Calculator()
    return calculator.calculate(filepath)


def calculate_sha256(filepath):
    calculator = Sha256Calculator()
    return calculator.calculate(filepath)


def parse_json_manifest(filepath):
    parser = JsonManifestParser()
    return parser.parse(filepath)


def parse_xml_manifest(filepath):
    parser = XmlManifestParser()
    return parser.parse(filepath)


def normalize_checksum(checksum, checksum_type):
    if not checksum:
        return ""

    checksum = str(checksum).strip().lower()

    if checksum.startswith('0x'):
        checksum = checksum[2:]


    checksum = checksum.replace(' ', '')

    return checksum


def check_checksums(manifest_path):


    print(f"проверяем файл: {manifest_path}")
    print("-" * 60)

    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        print(f"файл не найден: {manifest_path}")
        return False


    if manifest_path.suffix.lower() == '.json':
        try:
            files_to_check = parse_json_manifest(manifest_path)
        except json.JSONDecodeError as e:
            print(f"ошибка парсинга JSON: {e}")
            return False
    elif manifest_path.suffix.lower() == '.xml':
        try:
            files_to_check = parse_xml_manifest(manifest_path)
        except ET.ParseError as e:
            print(f"ошибка парсинга XML: {e}")
            return False
    else:
        print(f"неподдерживаемый формат файла: {manifest_path.suffix}")
        print("поддерживаются только .json и .xml файлы")
        return False

    if not files_to_check:
        print("в JSON файле не найдены файлы для проверки")
        return True

    print(f"найдено {len(files_to_check)} файл(ов) для проверки")
    print("-" * 60)

    all_ok = True
    failed_files = []

    for i, file_info in enumerate(files_to_check, 1):
        filename = file_info['filename']
        expected = file_info['expected']
        checksum_type = file_info['type']

        print(f"{i}. Файл: {filename}")
        print(f"ожидаемая контрольная сумма ({checksum_type}): {expected}")


        if not os.path.exists(filename):
            print(f"файл не найден!")
            all_ok = False
            failed_files.append(f"{filename} (файл не найден)")
            print()
            continue

        calculator = ChecksumCalculatorFactory.get_calculator(checksum_type)

        if calculator is None:
            print(f"неподдерживаемый тип контрольной суммы: {checksum_type}")
            print()
            continue

        actual = calculator.calculate(filename)

        if checksum_type == 'crc32':
            actual = calculate_crc32(filename)
            if actual is not None:
                actual_hex = f"{actual:08x}"
        elif checksum_type == 'md5':
            actual = calculate_md5(filename)
            actual_hex = actual
        elif checksum_type == 'sha256':
            actual = calculate_sha256(filename)
            actual_hex = actual
        else:
            print(f"неподдерживаемый тип контрольной суммы: {checksum_type}")
            print(f"пропускаем проверку этого файла")
            print()
            continue

        if actual is None:
            print(f"не удалось найтии контрольную сумму")
            all_ok = False
            failed_files.append(f"{filename} (ошибка вычисления)")
            print()
            continue


        expected_normalized = normalize_checksum(expected, checksum_type)
        actual_normalized = normalize_checksum(actual_hex, checksum_type)


        if expected_normalized == actual_normalized:
            print(f"совпало")
        else:
            print(f"не совпало")
            print(f"должно быть: {actual_hex}")
            all_ok = False
            failed_files.append(filename)

        print()


    print("=" * 60)
    if all_ok:
        print("все контрольные суммы совпадают!")
        return True
    else:
        print("обнаружены несовпадения контрольных сумм:")
        for failed in failed_files:
            print(f"   - {failed}")
        return False


def main():

    parser = argparse.ArgumentParser(description="утилита для проверки контрольных сумм файлов")
    parser.add_argument('manifest', help='путь к файлу манифеста (JSON или XML)')
    args = parser.parse_args()

    success = check_checksums(args.manifest)


    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
