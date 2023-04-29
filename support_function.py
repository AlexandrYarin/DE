from selenium.webdriver.common.by import By
import time
import os
import numpy as np


config = np.load('parser_config.npy', allow_pickle=True).item()

def write_head_table(file: object, table_head:object) -> None:
    
    title_table = []
                
    for col in table_head:
        if col.text: title_table.append(col.text)
        else: title_table.append('None')
    
    file.write(';'.join(title_table) + '\n')


def write_data_table(file:object, strings: object) -> None:
    for string in strings:
        cols = string.find_elements(By.TAG_NAME, 'td')
        data = []
        for col in cols:
            if col.text:
                data.append(col.text.replace('\n', ' '))
            else:
                data.append('None')
        file.write(';'.join(data) + '\n')


def get_links_series(driver: object) -> list:
    
    button = driver.find_element(By.XPATH, config['BUTTON_SERIES_XP'])
    button.click()
    time.sleep(3)
    menu_series = driver.find_element(By.XPATH, config['GRID_SERIES_XP'])
    time.sleep(3)
    series_items = menu_series.find_elements(By.TAG_NAME, 'a')

    links = [elem.get_attribute('href') for elem in series_items]

    return links    


def check_path(path:str) -> bool:
    
    """Проверка на наличие данной таблицы
    Если таблица уже существует, то не парсим дальше"""

    if os.path.exists(path) and os.stat(path).st_size != 0:
        return True
    else:
        return False