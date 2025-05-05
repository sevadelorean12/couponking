from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import os


service = Service(executable_path=r'C:\Users\HYPERPC\Desktop\BURGER\yandexdriver.exe')
driver = webdriver.Chrome(service=service)
menu_file = 'menu_items.txt'


def load_menu_items():
    if not os.path.exists(menu_file):
        return {}

    menu_items = {}
    with open(menu_file, 'r', encoding='utf8') as file:
        for line in file:
            name, price = line.strip().split(':')
            if price != 'Not on menu':
                menu_items[name] = float(price)
            else:
                menu_items[name] = 0
    return menu_items


menu_items = load_menu_items()


def save_menu_item(name, price):
    with open(menu_file, 'a', encoding='utf8') as file:
        file.write(f"{name}:{price}\n")
    if price != 'Not on menu':
        menu_items[name] = float(price)
    else:
        menu_items[name] = 0


def open_bk(link = 'https://burgerkingrus.ru'):
    driver.get(link)
    time.sleep(0.4)
    try:
        geo_popup = driver.find_element(By.CLASS_NAME, 'bk-order-point-info__geolocation-permission')
        close_button = geo_popup.find_element(By.CLASS_NAME, 'block-close')
        close_button.click()
        time.sleep(0.2)
    except Exception:
        print("Geolocation popup did not appear")
    try:
        cookie_popup = driver.find_element(By.CLASS_NAME, 'bk-cookie-message')
        close_button = cookie_popup.find_element(By.CLASS_NAME, 'bk-cookie-message__submit')
        close_button.click()
        time.sleep(0.2)
    except Exception:
        print("Cookie message popup did not appear")
    print("Burger king site successfully opened")
    location_set_button = driver.find_element(By.CLASS_NAME, 'bk-order-point-info')
    location_set_button.click()
    time.sleep(0.3)
    dine_in_button = driver.find_element(By.CLASS_NAME, 'bk-order-type__restaurant')
    dine_in_button.click()
    time.sleep(0.2)
    search_input = driver.find_element(By.CLASS_NAME, 'bk-input__element')
    location = 'Атриум'
    search_input.send_keys(location)
    time.sleep(1)
    restaurant_location = driver.find_element(By.CLASS_NAME, 'bk-restaurant-card')
    restaurant_location.click()
    submit_button = driver.find_element(By.CLASS_NAME, 'bk-restaurants__submit-button')
    submit_button.click()
    time.sleep(0.4)
    print(f'Location "{location}" successfully set')


def get_menu_item_price(item_name):
    print(f"Looking for {item_name}...")
    saved_price = menu_items.get(item_name)
    if saved_price != 'Not on menu' and saved_price is not None:
        print(f"Found item {item_name}'s saved price = {saved_price}")
        return float(saved_price)
    elif saved_price == 'Not on menu':
        print(f"Item {item_name} is not on the menu")
        return 0
    print(f"Item {item_name} not saved, commencing search...")
    driver.get('https://burgerkingrus.ru')
    words = item_name.split()
    for i in range(len(words), 0, -1):
        search_string = ' '.join(words[:i])
        print(f"Searching for: {search_string}")
        try:
            search_input = driver.find_element(By.CLASS_NAME, 'ui-input-search')
            search_input.send_keys(Keys.CONTROL + 'a')
            search_input.send_keys(Keys.BACKSPACE)
            search_input.send_keys(search_string)
            time.sleep(0.4)
            searched_list = []
            try:
                searched_list = driver.find_element(By.CLASS_NAME, 'searched-list')
            except Exception as e:
                print(F'Could not find: {search_string}, shrinking inquiry...')
            if searched_list:
                results = searched_list.find_elements(By.CLASS_NAME, 'dish-cart-wrapper__info-content')
                for result in results:
                    name_chars = result.find_elements(By.TAG_NAME, 'span')
                    full_item_name = ''.join([char.text if char.text else ' ' for char in name_chars]).strip()
                    if item_name == full_item_name:
                        try:
                            price = price_element = result.find_element(By.CLASS_NAME, 'info-price')
                            price = price_element.text.strip()[:-2]
                            save_menu_item(item_name, price)
                            print(f"Successfully found: {item_name} at the price {price}")
                            return float(price)
                        except Exception as e:
                            print(f"Error extracting price: {e}")
                    if search_string == full_item_name:
                        result.click()
                        time.sleep(0.4)
                        try:
                            combo_popup = driver.find_element(By.CLASS_NAME, 'bk-popup--options-view')
                            if combo_popup:
                                driver.find_element(By.CLASS_NAME, 'bk-popup__close').click()
                                time.sleep(0.1)
                        except Exception:
                            pass
                        try:
                            taste_options = []
                            try:
                                taste_options = driver.find_elements(By.CLASS_NAME, 'bk-taste__name')
                            except Exception:
                                pass
                            if taste_options:
                                for taste_option in taste_options:
                                    taste_option.click()
                                    time.sleep(0.2)
                                    try:
                                        size_options = driver.find_elements(By.CLASS_NAME, 'bk-size')
                                    except Exception:
                                        title_element = driver.find_element(By.CLASS_NAME,
                                                                            'bk-order-common-manager__title')
                                        variant_title = title_element.text.strip()
                                        try:
                                            span_element = title_element.find_element(By.TAG_NAME, 'span')
                                            span_text = span_element.text.strip()
                                            variant_title = variant_title.replace(span_text, '').strip()
                                        except Exception:
                                            pass
                                        if variant_title == item_name:
                                            price_element = driver.find_element(By.CLASS_NAME,
                                                                                'bk-order-item-manager__buy')
                                            price = price_element.text.strip()
                                            price = float(price[price.find('•') + 1:price.find('₽')])
                                            save_menu_item(item_name, price)
                                            print(f"Successfully found: {item_name} at the price {price}")
                                            return price
                                    if size_options:
                                        for size_option in size_options:
                                            size_option.click()
                                            time.sleep(0.2)
                                            title_element = driver.find_element(By.CLASS_NAME, 'bk-order-common-manager__title')
                                            variant_title = title_element.text.strip()
                                            try:
                                                span_element = title_element.find_element(By.TAG_NAME, 'span')
                                                span_text = span_element.text.strip()
                                                variant_title = variant_title.replace(span_text, '').strip()
                                            except Exception:
                                                pass
                                            if variant_title == item_name:
                                                price_element = driver.find_element(By.CLASS_NAME, 'bk-order-item-manager__buy')
                                                price = price_element.text.strip()
                                                price = float(price[price.find('•') + 1:price.find('₽')])
                                                save_menu_item(item_name, price)
                                                print(f"Successfully found: {item_name} at the price {price}")
                                                return price
                                    else:
                                        title_element = driver.find_element(By.CLASS_NAME, 'bk-order-common-manager__title')
                                        variant_title = title_element.text.strip()
                                        try:
                                            span_element = title_element.find_element(By.TAG_NAME, 'span')
                                            span_text = span_element.text.strip()
                                            variant_title = variant_title.replace(span_text, '').strip()
                                        except Exception:
                                            pass
                                        if variant_title == item_name:
                                            price_element = driver.find_element(By.CLASS_NAME, 'bk-order-item-manager__buy')
                                            price = price_element.text.strip()
                                            price = float(price[price.find('•') + 1:price.find('₽')])
                                            save_menu_item(item_name, price)
                                            print(f"Successfully found: {item_name} at the price {price}")
                                            return price
                            else:
                                try:
                                    size_options = driver.find_elements(By.CLASS_NAME, 'bk-size')
                                except Exception:
                                    title_element = driver.find_element(By.CLASS_NAME,
                                                                        'bk-order-common-manager__title')
                                    variant_title = title_element.text.strip()
                                    try:
                                        span_element = title_element.find_element(By.TAG_NAME, 'span')
                                        span_text = span_element.text.strip()
                                        variant_title = variant_title.replace(span_text, '').strip()
                                    except Exception:
                                        pass
                                    if variant_title == item_name:
                                        price_element = driver.find_element(By.CLASS_NAME,
                                                                            'bk-order-item-manager__buy')
                                        price = price_element.text.strip()
                                        price = float(price[price.find('•') + 1:price.find('₽')])
                                        save_menu_item(item_name, price)
                                        print(f"Successfully found: {item_name} at the price {price}")
                                        return price
                                if size_options:
                                    for size_option in size_options:
                                        size_option.click()
                                        time.sleep(0.2)
                                        title_element = driver.find_element(By.CLASS_NAME,
                                                                            'bk-order-common-manager__title')
                                        variant_title = title_element.text.strip()
                                        try:
                                            span_element = title_element.find_element(By.TAG_NAME, 'span')
                                            span_text = span_element.text.strip()
                                            variant_title = variant_title.replace(span_text, '').strip()
                                        except Exception:
                                            pass
                                        if variant_title == item_name:
                                            price_element = driver.find_element(By.CLASS_NAME,
                                                                                'bk-order-item-manager__buy')
                                            price = price_element.text.strip()
                                            price = float(price[price.find('•') + 1:price.find('₽')])
                                            save_menu_item(item_name, price)
                                            print(f"Successfully found: {item_name} at the price {price}")
                                            return price
                                title_element = driver.find_element(By.CLASS_NAME, 'bk-order-common-manager__title')
                                variant_title = title_element.text.strip()
                                try:
                                    span_element = title_element.find_element(By.TAG_NAME, 'span')
                                    span_text = span_element.text.strip()
                                    variant_title = variant_title.replace(span_text, '').strip()
                                except Exception:
                                    pass
                                if variant_title == item_name:
                                    price_element = driver.find_element(By.CLASS_NAME, 'bk-order-item-manager__buy')
                                    price = price_element.text.strip()
                                    price = float(price[price.find('•') + 1:price.find('₽')])
                                    save_menu_item(item_name, price)
                                    print(f"Successfully found: {item_name} at the price {price}")
                                    return price
                            print(f"Could not found: {item_name}")
                            save_menu_item(item_name, 'Not on menu')
                            menu_items[item_name] = 0
                            return None
                        except Exception as e:
                            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
            save_menu_item(item_name, 'Not on menu')
            menu_items[item_name] = 0
            return None
    print(f"Could not found: {item_name}")
    save_menu_item(item_name, 'Not on menu')
    menu_items[item_name] = 0
    return None


def get_coupons():
    print('Commencing search for coupons...')
    coupons_dict = dict()
    driver.get('https://burgerkingrus.ru/coupon')
    time.sleep(0.3)
    coupons = driver.find_elements(By.CLASS_NAME, 'bk-coupon-item')
    for i, coupon in enumerate(coupons):
        price = float(coupon.find_element(By.CLASS_NAME, 'bk-coupon-item__price').text.strip()[:-2].replace(' ', ''))
        title = coupon.find_element(By.CLASS_NAME, 'bk-coupon-item__title').text.strip()
        coupon.click()
        time.sleep(0.6)

        try:
            popup = driver.find_element(By.CLASS_NAME, 'bk-popup__content')
            coupon_elements_normal = popup.find_elements(By.CLASS_NAME, 'bk-combo-component__name')
            coupon_elements_variable = popup.find_elements(By.CLASS_NAME, 'bk-combo-manager__component-checkbox')
            item_names = [item.text.strip() for item in coupon_elements_normal]
            for j, coupon_element_variable in enumerate(coupon_elements_variable):
                item_names = [item.text.strip() for item in coupon_elements_normal]
                coupon_element_variable.click()
                time.sleep(0.1)
                item_names += [coupon_element_variable.find_element(By.CLASS_NAME, 'bk-combo-manager__component-checkbox-title').text.strip()]
                price_element = driver.find_element(By.CLASS_NAME,
                                                    'bk-order-item-manager__buy')
                price = price_element.text.strip()
                price = float(price[price.find('•') + 1:price.find('₽')])
                price = round(price, 2)
                #                                              [item_names, price, actual_price, does_it_contain_unique_items]
                coupons_dict[title + f' (variation {j + 1})'] = [item_names, price, None, False]
            if not(coupon_elements_variable):
                coupons_dict[title] = [item_names, price, None, False]

        except Exception as e:
            print(f"An error occurred: {e}")

        close_button = driver.find_element(By.CLASS_NAME, 'bk-popup__close')
        close_button.click()
    print(f"Successfully parsed {len(coupons_dict)} variations of coupons")
    return coupons_dict


def evaluate(coupons_dict):
    print("Commencing evaluation")
    for coupon in coupons_dict:
        unique_items = False
        contents = coupons_dict[coupon][0]
        price = coupons_dict[coupon][1]
        actual_price = 0
        for item in contents:
            item_price = get_menu_item_price(item)
            if item_price != 'Not on menu' and item_price is not None and item_price != 0:
                actual_price += item_price
            else:
                unique_items = True
        if not unique_items:
            coupons_dict[coupon][2] = actual_price
        else:
            coupons_dict[coupon][2] = actual_price
            coupons_dict[coupon][3] = True
    print("Evaluation complete")
    return coupons_dict


open_bk()
coupons = get_coupons()
evaluated_coupons = evaluate(coupons)
evaluated_coupons_sorted = dict(sorted(evaluated_coupons.items(), key=lambda x: (x[1][2] - x[1][1]) / x[1][2] if x[1][2] != 0 else 0, reverse=True))
i = 0
for coupon in evaluated_coupons_sorted:
    if not evaluated_coupons_sorted[coupon][3]:
        i += 1
        contents = evaluated_coupons_sorted[coupon][0]
        price = evaluated_coupons_sorted[coupon][1]
        actual_price = evaluated_coupons_sorted[coupon][2]
        print(f"{i}. Coupon: {coupon}")
        print(f"Coupon's contents: {contents}")
        print(f"Coupon price: {round(price, 2)}")
        print(f"Actual price: {round(actual_price, 2)}")
        print(f"Profit: {round((actual_price - price) / actual_price, 4) * 100}%")

