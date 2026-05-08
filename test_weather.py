import pytest
import os
from weather_core import WeatherDiary

@pytest.fixture
def diary():
    """Фикстура с тестовым дневником."""
    d = WeatherDiary("test_weather.json")
    d.records = []
    d.next_id = 1
    yield d
    if os.path.exists("test_weather.json"):
        os.remove("test_weather.json")

@pytest.fixture
def populated_diary(diary):
    """Дневник с предзаполненными данными."""
    diary.add_record("01.01.2024", -5.0, "Снежно", True)
    diary.add_record("15.06.2024", 25.5, "Солнечно", False)
    diary.add_record("31.12.2024", -10.0, "Метель", True)
    return diary

# --- Позитивные тесты ---
class TestPositive:
    def test_add_valid_record(self, diary):
        result = diary.add_record("10.05.2024", 20.0, "Тепло и ясно", False)
        assert result is True
        assert len(diary.records) == 1
        assert diary.records[0]["temperature"] == 20.0
    
    def test_delete_existing_record(self, populated_diary):
        result = populated_diary.delete_record(2)
        assert result is True
        assert len(populated_diary.records) == 2
    
    def test_save_and_load(self, diary):
        diary.add_record("10.05.2024", 15.0, "Облачно", True)
        diary.save_to_file()
        
        new_diary = WeatherDiary("test_weather.json")
        assert len(new_diary.records) == 1
        assert new_diary.records[0]["description"] == "Облачно"
    
    def test_filter_by_date(self, populated_diary):
        filtered = populated_diary.filter_by_date("15.06.2024")
        assert len(filtered) == 1
        assert filtered[0]["temperature"] == 25.5
    
    def test_filter_by_temperature(self, populated_diary):
        filtered = populated_diary.filter_by_temperature(0.0)
        assert len(filtered) == 1
        assert filtered[0]["description"] == "Солнечно"

# --- Негативные тесты ---
class TestNegative:
    def test_invalid_date_format(self, diary):
        assert diary.add_record("2024-01-01", 10.0, "Тест", False) is False
        assert diary.add_record("31.13.2024", 10.0, "Тест", False) is False
        assert diary.add_record("01/01/2024", 10.0, "Тест", False) is False
    
    def test_non_numeric_temperature(self, diary):
        assert diary.add_record("01.01.2024", "тепло", "Тест", False) is False
        assert diary.add_record("01.01.2024", None, "Тест", False) is False
    
    def test_empty_description(self, diary):
        assert diary.add_record("01.01.2024", 10.0, "", False) is False
        assert diary.add_record("01.01.2024", 10.0, "   ", False) is False
    
    def test_invalid_precipitation_type(self, diary):
        assert diary.add_record("01.01.2024", 10.0, "Тест", "да") is False
        assert diary.add_record("01.01.2024", 10.0, "Тест", 1) is False
    
    def test_delete_nonexistent(self, populated_diary):
        assert populated_diary.delete_record(999) is False

# --- Граничные тесты ---
class TestBoundary:
    def test_extreme_temperatures(self, diary):
        assert diary.add_record("01.01.2024", -89.2, "Антарктида", False) is True
        assert diary.add_record("01.01.2024", 56.7, "Долина смерти", False) is True
        assert diary.add_record("01.01.2024", 0.0, "Ноль", True) is True
    
    def test_leap_year_date(self, diary):
        assert diary.add_record("29.02.2024", 0.0, "Високосный", False) is True
        assert diary.add_record("29.02.2023", 0.0, "Не високосный", False) is False
    
    def test_long_description(self, diary):
        long_desc = "Очень длинное описание погоды " * 50
        assert diary.add_record("01.01.2024", 20.0, long_desc, False) is True
