import pandas as pd

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import time
import os
import shutil
import logging
import gc

from support_function import get_links_series, check_path, write_head_table, write_data_table
from support_function import config


logging.basicConfig(
    level=logging.INFO, filename='logs.log',
    format='%(asctime)s %(levelname)s %(message)s'
    )


#STAGE_1 Launch and setings
#-------------------------------
logging.info('Stage#1')
years = list(range(2015, 2024))
options = Options()
options.add_argument('-headless')
driver = Chrome(options=options)
driver.get(config['HREF'])

try:
    series_links = get_links_series(driver)
    logging.info('Ссылки с сериями загрузились')
except Exception as e:
    logging.error(e, exc_info=True)

#STAGE_2 Load series links and their iterations
#-------------------------------
logging.info('Stage#2')
for link in series_links:
    for year in years:
        try:
            work_link = f'{link}{year}'
            driver.get(work_link)
            time.sleep(1)
            name_series = driver.find_element(By.CLASS_NAME, config['CLASS_NAME_SERIES']).text
        except Exception as e:
            logging.warning(f'У данной серии({link}) скорее всего нет результатов в {year} году')
            continue
        
        
        #создание директории при ее отсутсвии
        current_path = os.getcwd()
        
        main_path = f'{current_path}/data/{name_series}'
        if os.path.exists(main_path) is False: os.mkdir(main_path)
        
        var_path = f'{main_path}/{year}'
        if os.path.exists(var_path) is False: os.mkdir(var_path)
    
        #driver.get(work_link)
        #time.sleep(1)

#STAGE_3 Load links of race and their iteration
#-------------------------------
        logging.info('Stage#3')
        try:
            navig_races = driver.find_element(By.CLASS_NAME, config['CLASS_NAME_CALENDAR'])
            time.sleep(2)
        except NoSuchElementException:
            logging.warning(f'У данной серии({work_link}) в {year} году нет данных по гонкам')
            continue
        
        all_races = navig_races.find_elements(By.CLASS_NAME, config['CLASS_NAME_CALENDAR_ITEMS'])
        time.sleep(2)

        links_race = [elem.get_attribute('href') for elem in all_races]
        logging.info(f'Ссылки на гонки данной серии({work_link}) нашлись')
        
        for link_r in links_race:
            if link_r is not None:

                driver.get(link_r)
                time.sleep(1)
                race_name = driver.find_element(By.CLASS_NAME, config['CLASS_NAME_RACE']).text

                
                var_path = f'{main_path}/{year}/{race_name}'
                if os.path.exists(var_path) is False: os.mkdir(var_path)

#STAGE_4 Load links of races event and their iteration
#-------------------------------
                logging.info('Stage#4')
                navig_event = driver.find_element(By.CLASS_NAME, config['CLASS_NAME_MENU'])
                time.sleep(1)
                navig_events = navig_event.find_elements(By.TAG_NAME, 'a')

                links_part = [elem.get_attribute('href') for elem in navig_events]
                logging.info(f'Ссылки на ивенты данной гонки({link_r}) нашлись')

                for link_p in links_part:
                    if link is not None:
                        driver.get(link_p)
                        table_name = link_p[link_p.find('st=') + 3:].lower()
                    
                        tables = driver.find_elements(By.TAG_NAME, 'table')
                        
                        #Проверка на наличие готовых таблиц по данному пути
                        if len(tables) == 1:
                            result = check_path(f'{var_path}/{table_name}.csv')
                        else:
                            results = [check_path(f'{var_path}/{table_name}{i}.csv') for i in range(len(tables))]
                            result = sum(results)
                        
                        if result > 0: continue
            
#STAGE_5 Parsing table(s) and write in raw.txt
#-------------------------------
                        logging.info('Stage#5')
                        for i, table in enumerate(tables):
                            with open('raw.txt', 'w+') as file:
                                logging.info(f'На странице {link_p} все таблицы нашлись')

                                try:
                                    head = table.find_element(By.TAG_NAME, 'thead')
                                    table_head = head.find_elements(By.TAG_NAME, 'th')

                                    write_head_table(file, table_head)
                                except NoSuchElementException:
                                    logging.warning('У таблицы нет head')
                                    pass
                    
                                finally:
                                    body = table.find_element(By.TAG_NAME, 'tbody')
                                    strings = body.find_elements(By.TAG_NAME, 'tr')
                
                                    write_data_table(file, strings)
                            
                            true_path  = f'{var_path}/{table_name}{i}.csv' if result else f'{var_path}/{table_name}.csv'
                            #копирование данных из промежуточного текстового файла в .csv файл в готовую папку
                            logging.info(f'Копирование из raw.txt в {true_path}')
                            shutil.copyfile('raw.txt', true_path)
                    
                    else:
                        continue
            else:
                continue

    gc.collect()
logging.info('Программа завершена')





