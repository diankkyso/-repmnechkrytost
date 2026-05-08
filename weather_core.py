import json
import os
from datetime import datetime

class WeatherDiary:
    """Ядро дневника погоды с сохранением в JSON."""
    def __init__(self, filename="weather_data.json"):
        self.filename = filename
        self.records = []
        self.next_id = 1
        self.load_from_file()
    
    def load_from_file(self):
        """Загрузка записей из JSON-файла."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
                    self.next_id = data.get("next_id", 1)
            except (json.JSONDecodeError, FileNotFoundError):
                self.records = []
                self.next_id = 1
    
    def save_to_file(self):
        """Сохранение записей в JSON."""
        data = {
            "records": self.records,
            "next_id": self.next_id
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def get_records(self):
        """Возвращает копию списка записей."""
        return self.records.copy()
    
    def add_record(self, date: str, temperature: float, description: str, precipitation: bool) -> bool:
        """
        Добавляет запись о погоде.
        Валидация: date в формате ДД.ММ.ГГГГ, temperature — float, description — не пустая строка.
        """
        # Проверка даты
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except (ValueError, TypeError):
            return False
        
        # Проверка температуры
        if not isinstance(temperature, (int, float)):
            return False
        
        # Проверка описания
        if not isinstance(description, str) or not description.strip():
            return False
        
        # Проверка осадков
        if not isinstance(precipitation, bool):
            return False
        
        record = {
            "id": self.next_id,
            "date": date,
            "temperature": temperature,
            "description": description.strip(),
            "precipitation": precipitation
        }
        self.records.append(record)
        self.next_id += 1
        self.save_to_file()
        return True
    
    def delete_record(self, record_id: int) -> bool:
        """Удаляет запись по ID."""
        for record in self.records:
            if record["id"] == record_id:
                self.records.remove(record)
                self.save_to_file()
                return True
        return False
    
    def filter_by_date(self, date: str) -> list:
        """Возвращает записи за указанную дату."""
        return [r for r in self.records if r["date"] == date]
    
    def filter_by_temperature(self, min_temp: float) -> list:
        """Возвращает записи с температурой >= min_temp."""
        return [r for r in self.records if r["temperature"] >= min_temp]
