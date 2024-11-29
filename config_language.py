import yaml
import argparse
import sys
from pathlib import Path


class ConfigTranslator:
    def __init__(self, yaml_data):
        self.data = yaml_data
        self.resolved_data = {}

    def resolve_references(self, value):
        """Решает ссылки на другие значения (например, |key| -> значение key)."""
        if isinstance(value, str):
            # Заменяем все ссылки вида |key| на их значения
            while "|" in value:  # Поддержка множественных ссылок в строках
                for key in self.resolved_data:
                    value = value.replace(f"|{key}|", str(self.resolved_data[key]))
        return value

    def resolve_str_references(self, value):
        """Решает ссылки на другие значения внутри строковых значений (например, @"key" -> значение key)."""
        if isinstance(value, str):
            # Если это строка в формате @"key", то подставляем значение из переменных
            if value.startswith('@') and value != '@':
                key = value[1:]  # Убираем символ @
                if key in self.resolved_data:
                    value = str(self.resolved_data[key])  # Заменяем на значение переменной
        return value

    def translate_value(self, value, indent=0):
        """Переводит значение в нужный формат с учётом вложенности."""
        indent_space = "    " * indent  # Отступ для текущего уровня
        if isinstance(value, str):
            # Резолвим переменные в строках, включая @key формы
            resolved_value = self.resolve_str_references(value)
            return f'@"{resolved_value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            # Обработка массива
            items = [self.translate_value(v, indent + 1) for v in value]
            return f"{{ {'. '.join(items)}. }}"
        elif isinstance(value, dict):
            # Обработка словаря
            entries = ",\n".join(
                f"{indent_space}{key} = {self.translate_value(val, indent + 1)}"
                for key, val in value.items()
            )
            return f"dict(\n{entries}\n{indent_space})"
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    def translate(self, indent=0):
        """Переводит YAML в формат учебного языка с учётом вычисления значений."""
        indent_space = "    " * indent
        output = []
        for key, value in self.data.items():
            # Проверяем корректность имени
            if not self.is_valid_identifier(key):
                raise SyntaxError(f"Invalid key name: {key}")
            
            # Резолвим значения для констант
            resolved_value = self.resolve_references(value)
            # Запоминаем вычисленные значения для возможных ссылок
            self.resolved_data[key] = resolved_value
            # Переводим значение
            translated_value = self.translate_value(resolved_value, indent + 1)
            # Формируем строку
            output.append(f"{indent_space}def {key} = {translated_value};")
        return "\n".join(output)

    def is_valid_identifier(self, name):
        """Проверяет, является ли имя допустимым идентификатором согласно правилам языка."""
        return bool(name) and name[0].isalpha() and all(c.isalnum() or c == '_' for c in name)


def main():
    parser = argparse.ArgumentParser(description="YAML to Config Translator")
    parser.add_argument("input_file", help="Path to the input YAML file.")
    parser.add_argument("output_file", help="Path to the output file where the result will be saved.")
    args = parser.parse_args()

    # Чтение YAML из входного файла
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with input_path.open("r", encoding="utf-8") as input_file:
            yaml_data = yaml.safe_load(input_file)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(yaml_data, dict):
        print("Root YAML element must be a dictionary.", file=sys.stderr)
        sys.exit(1)

    # Перевести YAML в формат учебного конфигурационного языка
    try:
        translator = ConfigTranslator(yaml_data)
        translated_output = translator.translate()
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}", file=sys.stderr)
        sys.exit(1)

    # Записать результат в выходной файл
    output_path = Path(args.output_file)
    try:
        with output_path.open("w", encoding="utf-8") as output_file:
            output_file.write(translated_output)
        print(f"Translation completed successfully. Output written to {args.output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
