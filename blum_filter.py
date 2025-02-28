import mmh3
import bitarray


class BloomFilter:
    """
    Реалізація фільтра Блума для перевірки унікальності паролів.
    Використовує `bitarray` для економії пам'яті та `mmh3` для хешування.
    """

    def __init__(self, size: int, num_hashes: int):
        """
        Ініціалізує фільтр Блума.

        Args:
            size (int): Розмір бітового масиву.
            num_hashes (int): Кількість хеш-функцій.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)

    def _hashes(self, item: str):
        """
        Генерує `num_hashes` хешів для заданого рядка.

        Args:
            item (str): Рядок, для якого генеруються хеші.

        Returns:
            list[int]: Список хешів.
        """
        return [mmh3.hash(item, seed) % self.size for seed in range(self.num_hashes)]

    def add(self, item: str):
        """
        Додає елемент у фільтр Блума.

        Args:
            item (str): Рядок, який додається у фільтр.
        """
        for hash_value in self._hashes(item):
            self.bit_array[hash_value] = 1

    def check(self, item: str) -> bool:
        """
        Перевіряє, чи є елемент у фільтрі (можливі хибнопозитивні спрацювання).

        Args:
            item (str): Рядок, що перевіряється.

        Returns:
            bool: `True`, якщо елемент може бути у фільтрі, `False` - якщо точно відсутній.
        """
        return all(self.bit_array[hash_value] for hash_value in self._hashes(item))


def check_password_uniqueness(bloom_filter: BloomFilter, passwords: list) -> dict:
    """
    Перевіряє список паролів на унікальність, використовуючи фільтр Блума.

    Args:
        bloom_filter (BloomFilter): Екземпляр фільтра Блума.
        passwords (list): Список паролів для перевірки.

    Returns:
        dict: Словник з паролями як ключами і статусом ('унікальний', 'вже використаний', 'некоректний пароль').
    """
    results = {}
    for password in passwords:
        if not isinstance(password, str) or not password.strip():
            results[password] = "некоректний пароль"
        elif bloom_filter.check(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom_filter.add(password)
    return results


if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")
