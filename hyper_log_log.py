import json
import time
from hyperloglog import HyperLogLog


def load_ips_from_log(file_path):
    """Завантажує IP-адреси з лог-файлу.
    
    Args:
        file_path (str): Шлях до файлу логів.
        
    Returns:
        list: Список IP-адрес.
    """
    ip_addresses = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                log_entry = json.loads(line)
                ip = log_entry.get("remote_addr")
                if ip:
                    ip_addresses.append(ip)
            except json.JSONDecodeError:
                continue
    return ip_addresses


def set_count(ip_addresses):
    """Підрахунок унікальних IP-адрес за допомогою set.
    
    Args:
        ip_addresses (list): Список IP-адрес.
        
    Returns:
        int: Кількість унікальних IP-адрес.
    """
    return len(set(ip_addresses))


def hll_count(ip_addresses):
    """Підрахунок унікальних IP-адрес за допомогою HyperLogLog.
    
    Args:
        ip_addresses (list): Список IP-адрес.
        
    Returns:
        float: Приблизна кількість унікальних IP-адрес.
    """
    hll = HyperLogLog(0.005)  # 0.5% похибка
    for ip in ip_addresses:
        hll.add(ip)
    return len(hll)


def compare_methods(ip_addresses):
    """Порівнює продуктивність підрахунку з set та HyperLogLog.
    
    Args:
        ip_addresses (list): Список IP-адрес.
        
    Returns:
        dict: Результати порівняння.
    """
    start_time = time.time()
    set_result = set_count(ip_addresses)
    set_time = round(time.time() - start_time, 3)
    
    start_time = time.time()
    hll_result = hll_count(ip_addresses)
    hll_time = round(time.time() - start_time, 3)
    
    return {
        "Унікальні елементи": {"Точний підрахунок": set_result, "HyperLogLog": hll_result},
        "Час виконання (сек.)": {"Точний підрахунок": set_time, "HyperLogLog": hll_time}
    }


if __name__ == "__main__":
    file_path = "lms-stage-access.log"
    ip_addresses = load_ips_from_log(file_path)
    results = compare_methods(ip_addresses)
    
    # Виведення результатів порівняння
    print("Результати порівняння:")
    print(f"{'':<25}{'Точний підрахунок':<20}{'HyperLogLog':<20}")
    for metric, values in results.items():
        print(f"{metric:<25}{values['Точний підрахунок']:<20}{values['HyperLogLog']:<20}")