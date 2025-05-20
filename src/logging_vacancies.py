###########################################################################
import logging
import os
from logging.handlers import RotatingFileHandler

# Создаем люггер с уровнем DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Настройка формата сообщений
formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s — %(funcName)s- %(levelname)s - %(message)s")

# Создание обработчика для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

# Создание обработчика для записи в файл
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/decorators.logs")
file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 10, backupCount=5)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.WARNING)

# Добавление обработчиков
logger.addHandler(file_handler)
logger.addHandler(console_handler)

###########################################################################
