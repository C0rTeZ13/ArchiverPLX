import os.path
import struct
from huffman import *


def file_encode():
    fileCount = int(input("Введите количество кодируемых файлов: "))
    archive_name = input("Введите название получаемого архива (без формата): ")
    archive_name += '.plx'

    data_files = list()
    fileSizes = list()
    fileNames = list()
    for i in range(fileCount):
        fileNames.append(input("Введите название кодируемого файла (с форматом): "))
        f = open(fileNames[i], 'rb')
        data_files.append(f.read())
        fileSizes.append(os.path.getsize(fileNames[i]))
        f.close()

    print("1. Сжатие методом Хаффмана.\nЛюбое другое значение - без сжатия.")
    check = input("Введите значение: ")
    if check == '1':
        data_files_coded = huffman_encode(data_files)  # Сжатие файла
        algorythmCode = b'\x00\x01'
    else:
        data_files_coded = data_files
        algorythmCode = b'\x00\x00'

    archive = open(archive_name, 'wb')
    signature = b'\xff\xbb\xaa\xcc'
    version = b'\x02'
    archive.write(signature + version + algorythmCode + fileCount.to_bytes(4, 'big'))
    for j in range(fileCount):
        default_size = fileSizes[j].to_bytes(4, 'big')
        real_size = len(data_files_coded[j]).to_bytes(4, 'big')
        filename_to_bytes = bytes(fileNames[j], 'utf-8')
        countOfBytes = len(fileNames[j].encode('utf-8'))
        zero_bytes = b''
        if countOfBytes > 16:
            print("Error very long name")
        else:
            for i in range(16 - countOfBytes):
                zero_bytes += b'\x00'
            archive.write(default_size + real_size + zero_bytes + filename_to_bytes + data_files_coded[j])
    archive.close()


def file_decode(archive_name):
    archive = open(archive_name, 'rb')
    count = 1
    files_count_byte = b''
    archiveSignature = b''
    algorythmCode = b''
    while byte := archive.read(1):
        if 1 <= count <= 4:
            archiveSignature += byte
        if 6 <= count <= 7:
            algorythmCode += byte
        if 8 <= count <= 11:
            files_count_byte += byte
        if count > 15:
            break
        count += 1
    if archiveSignature != b'\xff\xbb\xaa\xcc':
        print("Сигнатура архива неверна или отсутствует.\nПрекращение работы программы.")
        exit()
    files_count = int.from_bytes(files_count_byte, 'big')

    count = 11
    for fileNum in range(files_count):
        file_default_size_bytes = b''
        file_real_size_bytes = b''
        fileName = b''
        fileData = b''
        for a in range(count, count + 4):
            archive.seek(a)
            file_default_size_bytes += archive.read(1)
        for r in range(count + 4, count + 8):
            archive.seek(r)
            file_real_size_bytes += archive.read(1)
        file_real_size = int.from_bytes(file_real_size_bytes, 'big')
        for b in range(count + 8, count + 24):
            archive.seek(b)
            fileName += archive.read(1)
        for c in range(count + 24, count + 24 + file_real_size):
            archive.seek(c)
            fileData += archive.read(1)
        if algorythmCode == b'\x00\x01':
            fileDataDecoded = huffman_decode(fileData, file_default_size_bytes)
        else:
            fileDataDecoded = fileData
        file = open(fileName.decode('utf-8').replace('\00', ''), 'wb')
        file.write(fileDataDecoded)
        file.close()
        count += 24 + file_real_size
    archive.close()


while True:
    print("1. Кодировать файлы")
    print("2. Декодировать файл")
    print("Введите любой другой символ, чтобы выйти.")
    choice = input("Выберите опцию: ")
    if choice == '1':
        file_encode()
    elif choice == '2':
        archiveName = input("Введите имя архива (без формата): ")
        archiveName += '.plx'
        file_decode(archiveName)
    else:
        break
