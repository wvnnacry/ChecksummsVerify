# ChecksummsVerify
утилита для проверки контрольный сумм *JSON* файлов


### ***Состав***
1. change_text.py - изменяет текст в текстовиках (file1.txt file2.txt file3.txt) на случайный
2. manifest_maker.py - автоматически создает msnifest.json, содержащий хеш-суммы текстовиков, о которых мы говорили ранее
3. test_simple.py - является тестом, проверяет что manifest.json правильно читается и обновляется
4. tinker.py - итоговая промграмма для проверки контрольных сумм

### Использование
все программы можно использовать в cmd/PowerShell
1) python change_text.py - изменить все текстовые файлы
#
1.1) python change_text.py file1.txt file2.txt - изменить отдельные текстовые файлы
#
2) python manifest_maker.py - создать manifest.json
#
3) python test_simple.py - выполнить тестирование
#
4) python tinker.py manifest.json - вычислить контрольную сумму manifest.json

#
*Можете использовать папку с тестовыми файлами, которые использовал я* (прикреплена к репозиторию)

#
![для удобства я положил все файлы в одну папку:](https://github.com/wvnnacry/ChecksummsVerify/blob/main/image.png?raw=true)



**для удобства я положил все файлы в одну папку**
