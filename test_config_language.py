import yaml
from pathlib import Path
from config_language import ConfigTranslator


def generate_config(input_file, output_file):
    """Функция для генерации .config из YAML."""
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Читаем YAML
    try:
        with input_path.open("r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
    except Exception as e:
        print(f"Ошибка при чтении файла {input_file}: {e}")
        return False

    # Переводим YAML в конфигурационный язык
    try:
        translator = ConfigTranslator(yaml_data)
        translated_output = translator.translate()
    except Exception as e:
        print(f"Ошибка при трансляции файла {input_file}: {e}")
        return False

    # Записываем результат в .config файл
    try:
        with output_path.open("w", encoding="utf-8") as file:
            file.write(translated_output)
    except Exception as e:
        print(f"Ошибка при записи файла {output_file}: {e}")
        return False

    print(f"Файл {output_file} успешно создан.")
    return True


if __name__ == "__main__":
    examples = [
        ("examples/example1.yaml", "examples/example1.config"),
        ("examples/example2.yaml", "examples/example2.config"),
        ("examples/example3.yaml", "examples/example3.config"),
    ]

    all_passed = True
    for input_file, output_file in examples:
        print(f"Обработка файла {input_file}...")
        if not generate_config(input_file, output_file):
            all_passed = False

    if all_passed:
        print("\nВсе конфигурации успешно созданы.")
    else:
        print("\nНекоторые конфигурации не удалось создать.")
