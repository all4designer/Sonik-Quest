import requests
from collections import defaultdict


def fetch_all_transmitters():
    base_url = "https://sonik.space/api/transmitters/"
    session = requests.Session()
    transmitters = []
    page = 1
    while True:
        try:
            response = session.get(base_url, params={'page': page})
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            transmitters.extend(data)
            page += 1
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break
            else:
                raise

    return transmitters


def find_max_transmitters_satellite(transmitters):
    satellite_transmitters = defaultdict(list)

    for tx in transmitters:
        norad = tx['satellite_norad']
        satellite_transmitters[norad].append(tx)

    max_norad = None
    max_count = 0

    for norad, txs in satellite_transmitters.items():
        if len(txs) > max_count:
            max_count = len(txs)
            max_norad = norad

    if max_norad is None:
        return None, None, 0

    satellite_name = txs[0]['satellite_name'] if txs else "Unknown"
    return max_norad, satellite_name, max_count


def find_best_transmitter(transmitters):
    best_tx = None
    best_percentage = -1.0

    for tx in transmitters:
        stat = tx.get('stat', {})
        total = stat.get('total_count', 0)
        good = stat.get('good_count', 0)

        if total == 0:
            percentage = 0.0
        else:
            percentage = (good / total) * 100

        if percentage > best_percentage:
            best_percentage = percentage
            best_tx = tx

    return best_tx, best_percentage


def main():
    print(f"====================================\n\n")
    print("Загрузка, пожалуйста подождите...")
    transmitters = fetch_all_transmitters()
    if not transmitters:
        print("Нет данных о передатчиках.")
        return
    print(f"\n\n====================================\n\n")
    print("Данные успешно получены. Идет обработка...")

    norad_id, name, count = find_max_transmitters_satellite(transmitters)
    if norad_id is None:
        print("Не удалось определить спутник.")
        return

    satellite_txs = [tx for tx in transmitters if tx['satellite_norad'] == norad_id]
    best_tx, success_rate = find_best_transmitter(satellite_txs)
    print(f"\n\n====================================\n\n")

    print(f"Спутник с наибольшим числом передатчиков:")
    print(f"  Название: {name}")
    print(f"  NORAD ID: {norad_id}")
    print(f"  Количество передатчиков: {count}\n")

    if best_tx:
        print("Лучший передатчик по успешным наблюдениям:")
        print(f"  UUID: {best_tx['uuid']}")
        print(f"  Описание: {best_tx['description']}")
        print(f"  Тип: {best_tx['type']}")
        print(f"  Статус: {best_tx['status']}")
        print(f"  Успешные наблюдения: {success_rate:.2f}%")
    else:
        print("Нет данных о передатчиках для анализа.")


if __name__ == "__main__":
    main()