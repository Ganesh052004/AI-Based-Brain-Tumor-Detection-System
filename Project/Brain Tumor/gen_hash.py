import bcrypt
pw = bcrypt.hashpw(b'admin123', bcrypt.gensalt())
print(pw.decode())