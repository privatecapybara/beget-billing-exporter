# Beget Billing Exporter


## Принцип работы
Раз в определенное время (по-умолчанию 30 минут) делается запрос в [API Beget](https://beget.com/ru/kb/api/funkczii-upravleniya-akkauntom) для получения информации о текущем балансе аккаунта и количестве оставшихся дней до блокировки аккаунта за неуплату.

## Установка и запуск
### Предварительная подготовка
Необходимо установить API пароль в [панели управления Beget](https://cp.beget.com/settings/security/api).
В разделе "Разрешенные методы" необходимо включить пункт "Управление аккаунтом".

### Установка и запуск без контейнеризации
```bash
# Клонирование репозитория
git clone https://github.com/privatecapybara/beget-billing-exporter.git
cd beget-billing-exporter

# Создание виртуального окружения python
python -m venv venv
source ./venv/bin/activate

# Установка зависимостей
pip3 install -r requirements.txt

# Установка параметров
export BEGET_API_LOGIN="your_login"
export BEGET_API_PASSWORD="your_API_password"

# Запуск
python3 ./beget-billing-exporter.py
```

### Docker
```bash
docker run -d --name beget-billing-exporter -p 9481:9481 -e BEGET_LOGIN="your_login" -e BEGET_PASSWORD="your_API_password" ghcr.io/privatecapybara/beget-billing-exporter:latest
```

### Docker compose
```yaml
---
services:
  beget-billing-exporter:
    image: ghcr.io/privatecapybara/beget-billing-exporter:latest
    container_name: beget-billing-exporter
    ports:
      - "9481:9481"
    environment:
      - BEGET_API_LOGIN=your_login
      - BEGET_API_PASSWORD=your_API_password
    restart: unless-stopped
```

## Параметры 
Все параметры задаются через переменные окружения.

Обязательные параметры:
* **BEGET_API_LOGIN** - имя аккаунта
* **BEGET_API_PASSWORD** - пароль от API. Задается в [панели управления Beget](https://cp.beget.com/settings/security/api).

Опциональные параметры:
* **BEGET_API_URL** - URL для запроса. По-умолчанию: https://api.beget.com/api/user/getAccountInfo
* **BEGET_EXPORTER_PORT** - порт экспортера. По-умолчанию: 9481
* **BEGET_EXPORTER_SCRAPE_TIME** - частота обновления метрик (запросов в Beget). По-умолчанию: 1800 секунд (30 минут)

## Метрики
```bash
# HELP beget_user_balance_rub The user current balance in rubles
# TYPE beget_user_balance_rub gauge
beget_user_balance_rub{login="your_login"} 5000.00
# HELP beget_user_days_to_block Number of days before account blocking
# TYPE beget_user_days_to_block gauge
beget_user_days_to_block{login="your_login"} 30.0
```

## Настройка Prometheus
prometheus.yml:
```yaml
scrape_configs:
  - job_name: 'beget-billing'
    scrape_interval: 30m
    static_configs:
      - targets: ['beget-billing-exporter:9481']
```

## Пример настройки Alertmanager
alert.rules:
```yaml
groups:
  - name: beget-billing
    rules:
      - alert: BegetAccountCriticalBlock
        expr: beget_user_days_to_block <= 7
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Аккаунт Beget скоро будет заблокирован"
          description: |
            Аккаунт {{ $labels.login }} будет заблокирован через {{ $value }} дней.
            Текущий баланс: {{ with printf "beget_user_balance_rub{login=\"%s\"}" $labels.login | query }}{{ . | first | value }}{{ end }} руб.

      - alert: BegetCriticalLowBalance
        expr: beget_user_balance_rub <= 1000
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Низкий баланс аккаунта Beget"
          description: |
            Необходимо пополнить баланс аккаунта {{ $labels.login }}.
            Текущий баланс: {{ with printf "beget_user_balance_rub{login=\"%s\"}" $labels.login | query }}{{ . | first | value }}{{ end }} руб.
```
