import os

# Генерируем секретный ключ и записываем его в переменную окружения
secret_key = os.urandom(24)
with open(".env", "w") as f:
    f.write(f"SECRET_KEY={secret_key}\n")

print(f"Секретный ключ сгенерирован")
