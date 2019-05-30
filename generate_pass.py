from passlib.context import CryptContext
import sys
passwd = sys.argv[1]
setpw = CryptContext(schemes=['pbkdf2_sha512'])
print("Hash for '{}':".format(passwd))
print(setpw.encrypt(passwd))