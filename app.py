import platform
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import config
from config import logger
from sensor import find_device

# Inicjalizacja Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{config.DB_FILE.absolute()}"

scheduler = APScheduler()
scheduler.init_app(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Wpis do logów
class LogEntry(db.Model):
    id: Mapped[int] = mapped_column(autoincrement=True, unique=True, primary_key=True)
    temperature: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now, index=True)

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, temp={self.temperature} @{self.timestamp})>"


sensor = find_device()

with app.app_context():
    db.create_all()

chart_data: dict = {}
latest_measurement: tuple = ()


def format_temperature(milicelsius: int, precision: int, separator: str = ".") -> str:
    celsius = f"{(milicelsius / 1000):.{precision}f}".replace(".", separator)
    return celsius


# Strona główna
@app.route("/")
def root():
    if not latest_measurement:
        update_temp()

    logger.debug(chart_data)

    return render_template(
        "index.html",
        temp2f=latest_measurement[0],
        last_update=latest_measurement[1],
        t_data=chart_data,
    )


# Zwraca `n` najnowszych wpisów w bazie danych, posortowanych czasem wpisu rosnąco
@app.route("/logs")
def api_logs():
    n = request.args.get("n")
    if n:
        n = max(1, min(int(n), 250))
    else:
        n = 50
    q = LogEntry.query.order_by(LogEntry.timestamp.desc()).limit(n).all()[::-1]
    return jsonify(
        [
            {"temperature": line.temperature, "time": line.timestamp.isoformat()}
            for line in q
        ]
    )


# Zwraca aktualną temperaturę z czujnika w formacie JSON
# Zwraca temperaturę w milicelsjuszach
@app.route("/temperature")
def api_temp():
    with app.app_context():
        reading = sensor.read()
        logger.info(f"Endpoint `/temperature` hit. Aktualna temperatura: {reading}")
        return jsonify(
            {"temperature": reading, "timestamp": datetime.now().isoformat()}
        )


def update_temp():
    logger.info("update_temp() called")
    with app.app_context():
        global latest_measurement
        reading = sensor.read()
        if reading:
            latest_measurement = (
                format_temperature(reading, config.PRECISION),
                str(datetime.now()).split(".")[0],
            )

        else:
            logger.error("Temperature read request to server failed!")


def chart_from_db():
    print(chart_from_db)
    with app.app_context():
        global chart_data
        # aktualizacja wykresu
        q = (
            LogEntry.query.order_by(LogEntry.timestamp.desc())
            .limit(config.CHART_MAX_TICKS)
            .all()
        )

        chart_data = {}

        for entry in q:
            chart_data[str(entry.timestamp)] = float(
                format_temperature(entry.temperature, 3, ".")
            )


def log_temp():
    print("log_temp() called")
    with app.app_context():
        global latest_measurement

        reading = sensor.read()
        if r:
            entry = LogEntry()
            entry.temperature = r["temperature"]
            entry.timestamp = datetime.fromisoformat(r["timestamp"])

            db.session.add(entry)
            db.session.commit()

            # aktualizacja temperatury na stronie
            latest_temperature = (
                format_temperature(r["temperature"], config.PRECISION),
                r["timestamp"],
            )

            chart_from_db()
        else:
            logger.error("Temperature read request to server failed!")


os_name = platform.system()
if os_name.lower() != "linux":
    raise RuntimeError(
        f"Program może być uruchamiany tylko na systemach Linux! Wykryto: {os_name}"
    )


def run_with_context(func):
    with app.app_context():
        func()


if config.UPDATE_ON_START:
    run_with_context(log_temp)

run_with_context(chart_from_db)

scheduler.add_job(
    id="log_temp", func=log_temp, trigger="interval", seconds=config.LOGGING_INTERVAL
)
scheduler.add_job(
    id="update_temp", func=log_temp, trigger="interval", seconds=config.UPDATE_INTERVAL
)
scheduler.start()
