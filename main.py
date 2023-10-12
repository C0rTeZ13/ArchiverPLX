import os.path
import struct
from huffman import *


def file_encode():
    fileCount = int(input("Введите количество кодируемых файлов: "))
    archive_name = input("Введите название получаемого архива (без формата): ")
    archive_name += '.plx'

    dataFiles = list()
    fileSizes = list()
    fileNames = list()
    for i in range(fileCount):
        fileNames.append(input("Введите название кодируемого файла (с форматом): "))
        f = open(fileNames[i], 'rb')
        dataFiles.append(f.read())
        fileSizes.append(os.path.getsize(fileNames[i]))
        f.close()

    print("1. Сжатие методом Хаффмана.\nЛюбое другое значение - без сжатия.")
    check = input("Введите значение: ")
    if check == '1':
        dataFilesCoded = huffman_encode(dataFiles)  # Сжатие файла
    else:
        dataFilesCoded = dataFiles

    archive = open(archive_name, 'wb')
    signature = b'\xff\xbb\xaa\xcc'
    version = b'\x01'
    algorythmCode = b'\x00\x00'
    archive.write(signature + version + algorythmCode + fileCount.to_bytes(4, 'big'))
    for j in range(fileCount):
        defaultSize = struct.pack('>I', fileSizes[j] + 256)
        filenameToBytes = bytes(fileNames[j], 'utf-8')
        countOfBytes = len(fileNames[j].encode('utf-8'))
        zerobytes = b''
        if countOfBytes > 16:
            print("Error very long name")
        else:
            for i in range(16 - countOfBytes):
                zerobytes += b'\x00'
            archive.write(defaultSize + zerobytes + filenameToBytes + dataFilesCoded[j])
    archive.close()


def file_decode(archive_name):
    archive = open(archive_name, 'rb')
    count = 1
    fileCountByte = b''
    fileCount = 0
    archiveSignature = b''
    while byte := archive.read(1):
        if 1 <= count <= 4:
            archiveSignature += byte
        if 8 <= count <= 11:
            fileCountByte += byte
        if count > 11:
            break
        count += 1
    if archiveSignature != b'\xff\xbb\xaa\xcc':
        print("Сигнатура архива неверна или отсутствует.\nПрекращение работы программы.")
        exit()
    fileCount = fileCount.from_bytes(fileCountByte, 'big')

    count = 11
    for fileNum in range(fileCount):
        fileSize = b''
        fileSizeInt = 0
        fileName = b''
        fileData = b''
        for a in range(count, count + 4):
            archive.seek(a)
            fileSize += archive.read(1)
        fileSizeInt = fileSizeInt.from_bytes(fileSize, 'big')
        for b in range(count + 4, count + 20):
            archive.seek(b)
            fileName += archive.read(1)
        for c in range(count + 20, count + 20 + fileSizeInt):
            archive.seek(c)
            fileData += archive.read(1)
        fileDataDecoded = huffman_decode(fileData)
        file = open(fileName.decode('utf-8').replace('\00', ''), 'wb')
        file.write(fileData)
        file.close()
        count += 20 + fileSizeInt
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
