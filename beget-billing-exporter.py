import os
import time
import requests
from prometheus_client import start_http_server, Gauge

API_URL = os.getenv('BEGET_API_URL', 'https://api.beget.com/api/user/getAccountInfo')
LOGIN = os.getenv('BEGET_API_LOGIN')
PASSWORD = os.getenv('BEGET_API_PASSWORD')
PORT = int(os.getenv('BEGET_EXPORTER_PORT', 9481))
SCRAPE_TIME = int(os.getenv('BEGET_EXPORTER_SCRAPE_TIME', 1800))

USER_BALANCE = Gauge(
    'beget_user_balance_rub',
    'The user current balance in rubles',
    ['login']
)

USER_DAYS_TO_BLOCK = Gauge(
    'beget_user_days_to_block',
    'Number of days before account blocking',
    ['login']
)

def fetch_beget_data():
    try:
        params = {
            'login': LOGIN,
            'passwd': PASSWORD,
            'output_format': 'json'
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error while requesting Beget API: {e}")
        return None

def extract_metrics_from_response(data):
    if not data or data.get('status') != 'success':
        print("API response status is not 'success'")
        return None

    answer = data.get('answer', {})
    if answer.get('status') != 'success':
        print("Field 'answer' status is not 'success'")
        return None

    result = answer.get('result', {})

    balance = result.get('user_balance')
    days_to_block = result.get('user_days_to_block')

    if balance is None:
        print("Field 'user_balance' not found")
    if days_to_block is None:
        print("Field 'user_days_to_block' not found")

    return {
        'user_balance': balance,
        'user_days_to_block': days_to_block
    }

def update_metrics():
    data = fetch_beget_data()
    metrics = extract_metrics_from_response(data)

    if metrics is None:
        return

    if metrics['user_balance'] is not None:
        USER_BALANCE.labels(login=LOGIN).set(float(metrics['user_balance']))

    if metrics['user_days_to_block'] is not None:
        USER_DAYS_TO_BLOCK.labels(login=LOGIN).set(int(metrics['user_days_to_block']))


def main():
    update_metrics()
    start_http_server(PORT)
    print(f"HTTP service started on port {PORT}")

    while True:
        time.sleep(SCRAPE_TIME)
        update_metrics()

if __name__ == '__main__':
    if not LOGIN:
        raise ValueError("Required environment variable BEGET_API_LOGIN is not set")

    if not PASSWORD:
        raise ValueError("Required environment variable BEGET_API_PASSWORD is not set")

    main()
