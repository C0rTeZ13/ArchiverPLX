import heapq
from heapq import heappop, heappush
from collections import Counter

# Узел дерева
class Node:
    def __init__(self, ch, freq, left=None, right=None):
        self.ch = ch
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(freq):
    pq = [Node(byte, freq) for byte, freq in freq.items()]  # Создание приоритетной очереди

    heapq.heapify(pq)
    while len(pq) != 1:
        left = heappop(pq)
        right = heappop(pq)
        total = left.freq + right.freq
        heappush(pq, Node(None, total, left, right))

    return pq[0]


def huffman_decode(data, data_size):
    freq_str = b''
    encoded_data = b''
    for symbol_count in range(len(data)):
        if symbol_count < 256:
            freq_str += int(data[symbol_count]).to_bytes(1, "big")  # Строка с частотами
        else:
            encoded_data += int(data[symbol_count]).to_bytes(1, "big")  # Закодированная информация

    data_size = int.from_bytes(data_size, 'big')
    symbol_pos = 0
    freq = {}
    for symbol in freq_str:
        if symbol != 0:
            freq[symbol_pos] = symbol
        symbol_pos += 1

    root = build_huffman_tree(freq)
    decoded_data = bytearray()
    current_node = root

    # Проходим по каждому биту в закодированных данных
    for byte in encoded_data:
        # Перебираем биты в байте
        for i in range(8):
            if len(decoded_data) == data_size:
                break
            bit = (byte >> (7 - i)) & 1  # Получаем i-й бит
            if bit == 0:
                current_node = current_node.left  # Идем влево при 0
            else:
                current_node = current_node.right  # Идем вправо при 1

            if current_node.left is None and current_node.right is None:  # Дошли до листа, восстанавливаем символ
                decoded_data += current_node.ch.to_bytes(1, 'big')
                current_node = root  # Сбрасываем текущий узел к корню для нового символа

    return bytes(decoded_data)

def normalize(freq):
    new_freq = dict()
    for f in freq:
        if freq[f] > 0:
            new_freq[f] = round(((freq[f] - 1) / (max(freq.values()) - 1)) * (255 - 1)) + 1
    return new_freq


def huffman_encode(data_files):
    encoded_data_files = list()
    for i in range(len(data_files)):
        data = data_files[i]
        freq = {byte: data.count(byte) for byte in set(data)}  # Подсчет частот символов
        freq = normalize(freq)
        root = build_huffman_tree(freq)
        huffman_code = {}

        def encode(root, s):
            if root is None:
                return
            if root.ch is not None:
                huffman_code[root.ch] = s
            encode(root.left, s + '0')
            encode(root.right, s + '1')

        encode(root, '')

        # Подготовим данные для записи
        encoded_data = bytearray()
        for symbol in range(256):
            if symbol in freq:
                encoded_data.append(freq[symbol])
            else:
                encoded_data.append(0x00)

        # Записываем закодированные данные побитово
        current_byte = 0  # Текущий байт, который будем заполнять
        bit_position = 0  # Позиция текущего бита в байте

        for c in data:
            code = huffman_code[c]
            for bit in code:
                if bit == '1':
                    current_byte |= (1 << (7 - bit_position))

                bit_position += 1
                if bit_position == 8:
                    encoded_data.append(current_byte)
                    current_byte = 0
                    bit_position = 0

        # Добавляем последний байт (если есть неиспользованные биты)
        if bit_position > 0:
            encoded_data.append(current_byte)

        encoded_data_files.append(encoded_data)
    return encoded_data_files
