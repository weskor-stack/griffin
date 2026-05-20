import qrcode
import unicodedata

test = "P1895152/00/G\x3eSHG2242791000290"
test.encode("utf-8")
print(test.encode("utf-8"))
img = qrcode.make(test)
f = open("qr/test.png", "wb")
img.save(f)
f.close()