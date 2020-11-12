"""Программа по преобразованию файла, полученного из ВИМС, в csv-файл"""
import csv
import os


def read_file(file_input):
    with open(file_input, "r") as file:
        full_file = []
        for line in file.read().splitlines():
            full_file.append(line)
    return full_file


def write_file(output_path, names, data):
    with open(output_path, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(names)
        for line in data:
            writer.writerow(line)


def files_grubber():
    """Собирает все ascii файлы в текущей папке и передает их на чтение."""
    files_list = [datafile for datafile in os.listdir(".") if datafile.endswith("asc")]
    return files_list


def cut_datapoints(full_text):
    """Извлечение нужного содержимого из текста.
    Числа +3 и -1 нужны для отрезания всего лишнего;
    строки *** что-то *** - реперные точки - они всегда
    отделяют экспериментальные точки от настроек установки"""
    start_line = full_text.index("*** DATA START ***") + 3
    end_line = full_text.index("*** DATA END ***") - 1
    header = full_text[start_line]
    datapoints = full_text[start_line + 2 : end_line]
    return header, datapoints


def parse_ions_name(header):
    """Парсинг строки, содержащей названия ионов, разделенных
    табуляцией. Пробелы удаляются"""
    return [ion.replace(" ", "") for ion in filter(None, header.split("\t"))]


def get_original_filename(full_text):
    """Возвращает имя исходного файла. Имя находится на третьей строке"""
    name = full_text[2].split()[-1]
    return name.split(".")[0]


if __name__ == "__main__":

    files_list = files_grubber()
    for datafile in files_list:
        # чтение файла и извлечение нужных строк
        full_text = read_file(datafile)
        header, datapoints = cut_datapoints(full_text)

        # чтение имени файла
        output_file_prefix = get_original_filename(full_text)
        # чтение названий ионов
        elements = parse_ions_name(header)
        head = parse_ions_name(header)
        head.insert(0, "time")

        # чтение экспериментальных данных
        grid, data = [], []
        for line in datapoints:
            x, *y = map(float, line.split())
            # удаление дополнительных столбцов времён
            y = y[0::2]
            grid.append(x)
            data.append(y)

        # добавление в финальный файл столбец времени
        for i, j in enumerate(grid):
            data[i].insert(0, grid[i])

        # запись файла с именами столбцов
        file_output = output_file_prefix + ".csv"
        write_file(file_output, head, data)
