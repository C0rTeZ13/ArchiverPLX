import os.path
import struct
from arithmetic_compress import *
from arithmetic_decompress import *
from huffman import *
from file_encode_sum import *


def file_encode():
    fileCount = int(input("Введите количество кодируемых файлов: "))
    archive_name = input("Введите название получаемого архива (без формата): ")
    archive_name += '.plx'

    data_files = list()
    data_files_coded = list()
    fileSizes = list()
    fileNames = list()
    algorythmCodes = list()
    for i in range(fileCount):
        fileNames.append(input("Введите название кодируемого файла (с форматом): "))
        f = open(fileNames[i], 'rb')
        data_files.append(f.read())
        fileSizes.append(os.path.getsize(fileNames[i]))
        f.close()
        print("1. Сжатие методом Хаффмана.")
        print("2. Сжатие целочисленным интервальным алгоритмом.")
        print("Любое другое значение - без сжатия.\n")
        check = input("Введите значение: ")
        algorythmCode = b''
        data_file_coded = b''
        if check == '1':
            data_file_coded = huffman_encode(data_files[i])  # Сжатие файла методом Хаффмана
            if data_file_coded == data_files[i]:
                algorythmCode = b'\x00\x00'
            else:
                algorythmCode = b'\x00\x01'
        if check == '2':
            data_file_coded = arithmetic_compress(fileNames[i])  # Сжатие файла целочисленным интервальным методом
            if data_file_coded == data_files[i]:
                algorythmCode = b'\x00\x00'
            else:
                algorythmCode = b'\x00\x02'
        elif check != '1' and check != '2':
            data_file_coded = data_files[i]
            algorythmCode = b'\x00\x00'
        algorythmCodes.append(algorythmCode)
        data_files_coded.append(data_file_coded)

    archive = open(archive_name, 'wb')
    signature = b'\xff\xbb\xaa\xcc'
    version = b'\x02'
    archive.write(signature + version + fileCount.to_bytes(4, 'big'))
    for j in range(fileCount):
        algorythmCode = algorythmCodes[j]
        default_size = fileSizes[j].to_bytes(4, 'big')
        real_size = len(data_files_coded[j]).to_bytes(4, 'big')
        filename_to_bytes = bytes(fileNames[j], 'utf-8')
        countOfBytes = len(fileNames[j].encode('utf-8'))
        zero_bytes = b''
        if countOfBytes > 16:
            print("Ошибка, слишком длинное имя")
        else:
            for i in range(16 - countOfBytes):
                zero_bytes += b'\x00'
            archive.write(algorythmCode + default_size + real_size + zero_bytes + filename_to_bytes + data_files_coded[j])
    archive.close()


def file_decode(archive_name):
    archive = open(archive_name, 'rb')
    count = 1
    files_count_byte = b''
    archiveSignature = b''
    possible_algo = b''
    possible_size = b''
    while byte := archive.read(1):
        if 1 <= count <= 2:
            possible_algo += byte
        if 3 <= count <= 6:
            possible_size += byte
        if 1 <= count <= 4:
            archiveSignature += byte
        if 6 <= count <= 9:
            files_count_byte += byte
        if count > 13:
            break
        count += 1
    if archiveSignature != b'\xff\xbb\xaa\xcc':
        if possible_algo == b'\x00\x00':
            start_data = b''
            archive.seek(5)
            while byte := archive.read(1):
                start_data = archive.read()
            archive.close()
            archive = open(archive_name, 'wb')
            archive.write(start_data)
            archive.close()
            file_decode(archive_name)
            exit()
        if possible_algo == b'\x00\x01':
            start_data = b''
            archive.seek(5)
            while byte := archive.read(1):
                start_data = archive.read()
            archive.close()
            archive = open(archive_name, 'wb')
            archive.write(huffman_decode(start_data, possible_size))
            archive.close()
            file_decode(archive_name)
            exit()
        if possible_algo == b'\x00\x02':
            start_data = b''
            archive.seek(5)
            while byte := archive.read(1):
                start_data = archive.read()
            archive.close()
            tempfile_str = "new_tempfile"
            with open(tempfile_str, 'wb') as temp:
                temp.write(start_data)
            archive = open(archive_name, 'wb')
            archive.write(arithmetic_decompress(start_data))
            archive.close()
            os.remove(tempfile_str)
            file_decode(archive_name)
            exit()
        elif possible_algo != b'\x00\x00' and possible_algo != b'\x00\x01':
            print("Сигнатура архива неверна или отсутствует.\nПрекращение работы программы.")
            exit()
    files_count = int.from_bytes(files_count_byte, 'big')

    count = 9
    for fileNum in range(files_count):
        file_default_size_bytes = b''
        file_real_size_bytes = b''
        fileName = b''
        fileData = b''
        algorythmCode = b''
        for s in range(count, count + 2):
            archive.seek(s)
            algorythmCode += archive.read(1)
        for a in range(count + 2, count + 6):
            archive.seek(a)
            file_default_size_bytes += archive.read(1)
        for r in range(count + 6, count + 10):
            archive.seek(r)
            file_real_size_bytes += archive.read(1)
        file_real_size = int.from_bytes(file_real_size_bytes, 'big')
        for b in range(count + 10, count + 26):
            archive.seek(b)
            fileName += archive.read(1)
        for c in range(count + 26, count + 26 + file_real_size):
            archive.seek(c)
            fileData += archive.read(1)
        fileDataDecoded = b''
        if algorythmCode == b'\x00\x01':
            fileDataDecoded = huffman_decode(fileData, file_default_size_bytes)
        if algorythmCode == b'\x00\x02':
            fileDataDecoded = arithmetic_decompress(fileData)
        elif algorythmCode != b'\x00\x01' and algorythmCode != b'\x00\x02':
            fileDataDecoded = fileData
        file = open(fileName.decode('utf-8').replace('\00', ''), 'wb')
        file.write(fileDataDecoded)
        file.close()
        count += 26 + file_real_size
    archive.close()


while True:
    print("1. Кодировать файлы")
    print("2. Декодировать файл")
    print("Введите любой другой символ, чтобы выйти.")
    choice = input("Выберите опцию: ")
    if choice == '1':
        print("Включить для каждого файла собственный алгоритм кодирования?")
        print("y/n - ?")
        choice_2 = input("Выберите опцию: ")
        if choice_2 == 'y':
            file_encode()
            break
        if choice_2 == 'n':
            file_encode_sum()
            break
        else:
            print("Выход из программы")
            break
    elif choice == '2':
        archiveName = input("Введите имя архива (без формата): ")
        archiveName += '.plx'
        file_decode(archiveName)
    else:
        print("Выход из программы")
        break
