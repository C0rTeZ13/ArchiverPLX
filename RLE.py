def encode_RLE(data):
    count = 1
    result = []
    for i in range(1, len(data)):
        if data[i] != data[i - 1] or i == len(data) - 1:
            if count >= 4:
                result.append((data[i - 1], count, None))
            elif count >= 2:
                for _ in range(count):
                    result.append((data[i - 1], None, None))
            count = 1
        else:
            count += 1
    return result


def decode_RLE(data):
    result = []
    for item in data:
        if item[1] is not None:
            if item[2] is None:
                result.extend(bytes([item[0]]) * item[1])
            else:
                result.extend(bytes([item[0]]) * (item[1] + 3))
        else:
            result.append(item[0])
    return result


# Пример использования
data = bytes([1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0])
encoded_data = encode_RLE(data)
decoded_data = decode_RLE(encoded_data)

print("Исходные данные:", list(data))
print("Закодированные данные:", encoded_data)
print("Декодированные данные:", list(decoded_data))
