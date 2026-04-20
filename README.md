<h1 align="center">pi-temp-pbs</h1>
<p align="center">
    <a><img src="https://img.shields.io/badge/license-unlicense-gray?logo=unlicense&color=%23808080" /></a>
    <a><img src="https://img.shields.io/badge/license-unlicense-gray?logo=unlicense&color=%23808080" /></a>
</p>

Kod stworzony w ramach praktyk zawodowych, na Raspberry Pi 5.

Odczytuje temperaturę z czujnika DS18B20 podłączonego do interfejsu 1-wire, i za pomocą Pythona + Flask wyświetlą ją na frontendzie wraz z godzinnym wykresem z ostatniego dnia.

![Zrzut ekranu strony](readme/site.jpg)

### Wykorzystane technologie i języki:
- Python (Flask, APScheduler)
- Vanilla HTML, CSS, JS (Chart.JS)
- SQAlchemy, SQLite
- TOML (plik konfiguracji `config.toml`)
- Bash (skrypt `deploy.sh`)

### Wykorzystane przy deployment:
- nginx
- gunicorn
- systemd
