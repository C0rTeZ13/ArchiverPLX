import os

from huffman import huffman_encode


def file_encode_sum():
    fileCount = int(input("Введите количество кодируемых файлов: "))
    archive_name = input("Введите название получаемого архива (без формата): ")
    archive_name += '.plx'

    data_files = list()
    fileSizes = list()
    fileNames = list()
    algorythmCodes = list()
    for i in range(fileCount):
        fileNames.append(input("Введите название кодируемого файла (с форматом): "))
        f = open(fileNames[i], 'rb')
        data_files.append(f.read())
        fileSizes.append(os.path.getsize(fileNames[i]))
        f.close()
        algorythmCode = b'\x00\x00'
        algorythmCodes.append(algorythmCode)

    signature = b'\xff\xbb\xaa\xcc'
    version = b'\x02'
    end_data = signature + version + fileCount.to_bytes(4, 'big')
    for j in range(fileCount):
        algorythmCode = algorythmCodes[j]
        default_size = fileSizes[j].to_bytes(4, 'big')
        real_size = len(data_files[j]).to_bytes(4, 'big')
        filename_to_bytes = bytes(fileNames[j], 'utf-8')
        countOfBytes = len(fileNames[j].encode('utf-8'))
        zero_bytes = b''
        if countOfBytes > 16:
            print("Ошибка, слишком длинное имя")
        else:
            for i in range(16 - countOfBytes):
                zero_bytes += b'\x00'
            end_data += algorythmCode + default_size + real_size + zero_bytes + filename_to_bytes + data_files[j]

    print("1. Сжатие методом Хаффмана.")
    print("2. Сжатие целочисленным интервальным алгоритмом.")
    print("Любое другое значение - без сжатия.\n")
    check = input("Введите значение: ")
    algorythmCode_sum = b''
    data_file_coded_sum = b''
    if check == '1':
        data_file_coded_sum = huffman_encode(end_data)  # Сжатие файла методом Хаффмана
        if data_file_coded_sum == end_data:
            algorythmCode_sum = b'\x00\x00'
        else:
            algorythmCode_sum = b'\x00\x01'
    if check == '2':
        data_file_coded_sum = end_data  # Сжатие файла целочисленным интервальным методом
        if data_file_coded_sum == end_data:
            algorythmCode_sum = b'\x00\x00'
        else:
            algorythmCode_sum = b'\x00\x02'
    elif check != '1' and check != '2':
        data_file_coded_sum = end_data
        algorythmCode_sum = b'\x00\x00'
    archive = open(archive_name, 'wb')
    archive.write(algorythmCode_sum + len(end_data).to_bytes(4, 'big') + data_file_coded_sum)
    archive.close()
