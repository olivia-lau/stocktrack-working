#!/usr/bin/env python3

import csv
import datetime
import pickle
import re
import time
import pyautogui
import html2text
import psutil
import selenium
from selenium import webdriver
import sys

def startChrome():
    for p in psutil.process_iter():
        try:
            if 'Google Chrome' in p.name():
                p.kill()
        except psutil.Error:
            pass
            options = webdriver.ChromeOptions()
            options.add_argument("--user-data-dir=/Users/olivia/Library/Application Support/Google/Chrome Beta/")
            # options.add_argument("--profile-directory=Profile 2")
            # options.add_argument("--profile-directory=Default")
            # options.add_argument("--enable-accessibility-tab-switcher")
            options.add_argument("--disable-extensions")
            driver = webdriver.Chrome('/Users/olivia/chromedriver 2' , options=options)
            driver.set_page_load_timeout(10)
            return driver


def startChromeheadless():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/Users/olivia/Library/Application Support/Google/Chrome Beta/")
    # options.add_argument("--profile-directory=Default")
    options.add_argument("--enable-accessibility-tab-switcher")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    driver = webdriver.Chrome('/Users/olivia/chromedriver 2' , options=options)
    driver.set_page_load_timeout(10)
    return driver


    store_index_data = {
    'store_num':0,
    'store_name':1,
    'store_address':2,
    'store_distance':3,
    'store_price':4,
    'store_inventory':-1
    }
    stock_dict = {}




def pklsave(filename, content):
    with open(str(filename) + '.pkl', 'wb') as f:
        pickle.dump(content, f)


def pklopen(filename):
    with open(str(filename) + '.pkl', 'rb') as f:
        return pickle.load(f)


def list_postal_codes(path_to_source_pc, pkl_file_name):
    source_pc = path_to_source_pc
    area_checked = []
    final_list_to_checked = []
    with open(source_pc , 'r') as file:
        opened_file = csv.reader(file)
        for out in opened_file:
            for num, postal_code in enumerate(out):
                # print(num)
                postal_codes_area = postal_code[:3]
                if postal_codes_area not in area_checked:
                    final_list_to_checked.append(postal_code)
                    area_checked.append(postal_codes_area)
                    pklsave(pkl_file_name, final_list_to_checked)
                    return final_list_to_checked

list_product_info = []

def enter_fields(upc , loc , is_iter_one , num=2):
    field_dict = {'q': upc , 'loc': loc , 'num': num}
    form_control = driver.find_elements_by_class_name('dhxform_control')
    for classes in form_control:
        input_fields = classes.find_elements_by_tag_name('input')
        for input_field in input_fields:
            for field_key , field_var in field_dict.items():
                if input_field.get_attribute('name') == field_key:
                    field_id = input_field.get_attribute('id')
                    driver.find_element_by_id(field_id).clear()
                    driver.find_element_by_id(field_id).send_keys(field_dict[ field_key ])
                    # if field_key == 'loc':
                    #           time.sleep(1)
                    #           pyautogui.hotkey('down')
                    #           pyautogui.hotkey('return')
                    time.sleep(0.75)
                    driver.find_element_by_css_selector('#layoutObj > div > div:nth-child(1) > div.dhx_cell_cont_layout.dhx_cell_cont_no_borders > div > div > div:nth-child(1) > div.dhx_cell_cont_layout > div > div > div:nth-child(8) > div').click()
                    time.sleep(0.75)
                    if is_iter_one == 1:
                        product_info_raw = driver.find_element_by_css_selector('[id^=ListObject]').get_attribute('innerHTML')
                        product_img = ""
                        product_link = ""
                        product_name = ""
                        product_sku = ""
                        product_upc = "UPC: " + str(upc)
                        try:
                            product_img += re.search('<img src=\".+\.jpg\">', product_info_raw ).group(0)
                        except AttributeError:
                            pass
                        try:
                            product_link += re.search('<a href=\".+\"' , product_info_raw).group(0)
                        except AttributeError:
                            pass
                        try:
                            product_name += re.search('blank\">.+</a><br>' , product_info_raw).group(0)
                        except AttributeError:
                            pass
                        try:
                            product_sku += re.search('SKU: \d{13}' , product_info_raw).group(0)
                        except AttributeError:
                            pass
                        list_product_info.append(product_name[7:-8])
                        list_product_info.append(product_sku)
                        list_product_info.append(product_upc)
                        list_product_info.append( product_img[10:-2])
                        list_product_info.append(product_link[9:-17])
                        store_text_html = driver.find_element_by_css_selector('[id^=cgrid2]').get_attribute('innerHTML') # stock in closest 20 stores, \nName\nAddress\nDistance\nPrice\nStock\n
                        store_text_raw = html2text.html2text(store_text_html)
                        find_store_num = re.findall('\d{4}[^\s-]', store_text_raw)
                        store_text_split_list = [store_text_raw]
                        temp_delim = '____'
                        for num in find_store_num:
                            store_text_split_list.append(store_text_split_list[-1].replace(num, temp_delim + num))
                            list_stores = []
                            store_text_split_done = store_text_split_list[-1].split(temp_delim)
                            # print(store_text_split_done)
                            for row in store_text_split_done:
                                if '$' in row and 'innacurate' not in row:
                                    list_stores.append(row.replace('\n', ''))
                                    added_to_dict = 0
                                    for z in list_stores:
                                        b = z.replace('\n', '')
                                        new_row = b.split('|')
                                        fin_row = []
                                        for x in new_row:
                                            x = x.strip()
                                            if x != '':
                                                fin_row.append(x)
                                                if fin_row[store_index_data['store_num'] ] not in stock_dict:
                                                    stock_dict[fin_row[store_index_data['store_num'] ]] = (fin_row[store_index_data['store_name']]  , fin_row[store_index_data['store_address']], fin_row[store_index_data['store_price']]  , fin_row[store_index_data['store_inventory']])
                                                    added_to_dict += 1
                                                    print('Added to dict: ' + str(added_to_dict))
                                                    # for key, data in store_dict.items():
                                                    # 	print('{} - {}'.format(key, data))
                                                    return stock_dict, list_product_info


def test_scrape():
    enter_fields('7164110669', 'L4H 0R9')


def full_scrape(upc, openfile):
    postal_codes_checked = pklopen(openfile)
    for num, postal_codes in enumerate(postal_codes_checked):
        try:
            print(str(num) + ' of ' + str(len(postal_codes_checked)))
            # print(postal_codes)
            enter_fields(str(upc) , postal_codes, num)
            print('--------------------------------')
        except selenium.common.exceptions.ElementClickInterceptedException:
            break
            sort_name_stock_dict = {k: v for k , v in sorted(stock_dict.items() , key=lambda item: item[ 1 ][ 0 ])}
            sort_price_stock_dict = {k: v for k , v in sorted(stock_dict.items() , key=lambda item: item[ 1 ][ -2 ])}
            file_name = str(upc) + '_' + str(datetime.datetime.today()) + '.txt'
            try:
                with open(file_name, 'x') as f:
                    pass
            except FileExistsError:
                # with open(file_name , 'w') as f:
                pass
            finally:
                with open(file_name , 'w') as f:
                    for info in list_product_info:
                        f.write(info + '\n')
                        f.write('\n\n')
                        if len(sort_price_stock_dict.items()) == 0:
                            f.write('Stores w/ inventory: NONE \n')
                        else:
                            f.write('Stores w/ inventory:\n')
                            for key_store , data_store in sort_price_stock_dict.items():
                                if stock_dict[ key_store ][ -1 ] != '0':
                                    f.write('{} - {}\n'.format(key_store , data_store))
                                    f.write('\n\n')
                                    f.write('Stores Returned: {}\n'.format(str(len(stock_dict))))
                                    for key_store , data_store in sort_name_stock_dict.items():
                                        f.write('{} - {}\n'.format(key_store , data_store))
                                        f.write('\n\n')




# list_postal_codes('/Users/olivia/Downloads/Postal Codes 100 km Vaughan.csv', 'vaughan_area_codes')



start_time = time.time()
# driver = startChrome()
driver = startChromeheadless()
driver.get('https://stocktrack.ca/')
driver.switch_to.frame(driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/iframe'))
time.sleep(2)


full_scrape(sys.argv[0], '/Users/olivia/PycharmProjects/vaughan_area_codes')
print("--- %s seconds ---" % (time.time() - start_time))


# if __name__ == "__main__":
#     main()
