import openpyxl

if __name__ == '__main__':
    wb = openpyxl.load_workbook('wbs-zhangcy1.xlsx')
    sheet = wb.worksheets[0]
    for row in sheet.iter_rows():
        for cell in row:
            print(cell.coordinate, cell.value)