import contextlib, sys
import arithmeticcoding


def main():
    inputfile = "1.txt"
    outputfile = "output"

    freqs = get_frequencies(inputfile)
    freqs.increment(256)

    with open(inputfile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitout:
        write_frequencies(bitout, freqs)
        compress(freqs, inp, bitout)


def get_frequencies(filepath):
    freqs = arithmeticcoding.SimpleFrequencyTable([0] * 257)
    with open(filepath, "rb") as input:
        while True:
            b = input.read(1)
            if len(b) == 0:
                break
            freqs.increment(b[0])
    return freqs


def write_frequencies(bitout, freqs):
    for i in range(256):
        write_int(bitout, 32, freqs.get(i))


def compress(freqs, inp, bitout):
    enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
    while True:
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
    enc.write(freqs, 256)
    enc.finish()


def write_int(bitout, numbits, value):
    for i in reversed(range(numbits)):
        bitout.write((value >> i) & 1)


# Main launcher
if __name__ == "__main__":
    main()
