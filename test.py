import sys
import hashlib

hash_string = '2879283749283492839487593847953847593P1P2$1000'
encoded = hash_string.encode()
hashed = hashlib.sha256(encoded)
hex_hash = hashed.hexdigest()

print(encoded)
print(encoded[:2])

bin_format = "{0:08b}".format(int(encoded[:2], 16))
print(bin_format)

if bin_format[:2] == "0" * 2:
    print("True")
else:
    print("False")

bin_hash = bin(int(hex_hash[0], 16))[2:]

print(bin_hash)


