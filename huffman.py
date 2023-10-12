import heapq
from heapq import heappop, heappush


def is_leaf(root):
    return root.left is None and root.right is None


# Узел дерева
class Node:
    def __init__(self, ch, freq, left=None, right=None):
        self.ch = ch
        self.freq = freq
        self.left = left
        self.right = right

    # Переопределить функцию `__lt__()`, чтобы заставить класс `Node` работать с приоритетной очередью.
    # таким образом, что элемент с наивысшим приоритетом имеет наименьшую частоту
    def __lt__(self, other):
        return self.freq < other.freq


# Пройти по дереву Хаффмана и сохранить коды Хаффмана в словаре
def encode(root, s, huffman_code):
    if root is None:
        return

    # обнаружил листовой узел
    if is_leaf(root):
        huffman_code[root.ch] = s if len(s) > 0 else '1'

    encode(root.left, s + '0', huffman_code)
    encode(root.right, s + '1', huffman_code)


# Пройти по дереву Хаффмана и декодировать закодированную строку
def decode(root, index, s):
    if root is None:
        return index

    # обнаружил листовой узел
    if is_leaf(root):
        print(root.ch, end='')
        return index

    index = index + 1
    root = root.left if s[index] == '0' else root.right
    return decode(root, index, s)


# строит дерево Хаффмана и декодирует заданный входной текст
def build_huffman_tree(text):
    # Базовый случай: пустая строка
    if len(text) == 0:
        return

    # подсчитывает частоту появления каждого символа
    # и сохраните его в словаре
    freq = {byte: text.count(byte) for byte in set(text)}

    # Создайте приоритетную очередь для хранения активных узлов дерева Хаффмана.
    pq = [Node(byte, freq) for byte, freq in freq.items()]
    heapq.heapify(pq)

    # делать до тех пор, пока в queue не окажется более одного узла
    while len(pq) != 1:
        # Удалить два узла с наивысшим приоритетом
        # (самая низкая частота) из queue

        left = heappop(pq)
        right = heappop(pq)

        # создает новый внутренний узел с этими двумя узлами в качестве дочерних и
        # с частотой, равной сумме частот двух узлов.
        # Добавьте новый узел в приоритетную очередь.

        total = left.freq + right.freq
        heappush(pq, Node(None, total, left, right))

    # `root` хранит указатель на корень дерева Хаффмана.
    root = pq[0]

    # проходит по дереву Хаффмана и сохраняет коды Хаффмана в словаре.
    huffmanCode = {}
    encode(root, '', huffmanCode)
    # записать массив частот
    dataCoded = b''
    for symbol in range(256):
        if symbol in freq:
            dataCoded += int(freq[symbol]).to_bytes(1, 'big')
        else:
            dataCoded += b'\x00'

    # записать закодированное сообщение
    for c in text:
        dataCoded += int(huffmanCode.get(c)).to_bytes(1, 'big')

    if is_leaf(root):
        # Особый случай: для ввода типа a, aa, aaa и т. д.
        while root.freq > 0:
            print(root.ch, end='')
            root.freq = root.freq - 1
    return dataCoded


def huffman_decode(data):
    freq = b''
    dataDecoded = b''
    for symbol_count in range(len(data)):
        if symbol_count < 256:
            freq += int(data[symbol_count]).to_bytes(1, "big")
        else:
            dataDecoded += int(data[symbol_count]).to_bytes(1, "big")

    symbol_pos = 0
    freq_dict = {}
    for symbol in freq:
        freq_dict[symbol_pos] = symbol
        symbol_pos += 1
    print(freq_dict.items())
    return dataDecoded


def huffman_encode(data_files):
    dataFilesCoded = list()
    for i in range(len(data_files)):
        data = data_files[i]
        dataCoded = build_huffman_tree(data)
        dataFilesCoded.append(dataCoded)
    return dataFilesCoded
