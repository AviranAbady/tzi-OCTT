# MaEVe requires base64(sha256(password)) when setting a new charging point
# this can be used in ./maEVe-setup-csms.sh for generating the base64SHA256Password property

import hashlib
import base64

password = "password"
sha256pw = hashlib.sha256(password.encode()).digest()
b64sha256 = base64.b64encode(sha256pw).decode()

print(b64sha256)