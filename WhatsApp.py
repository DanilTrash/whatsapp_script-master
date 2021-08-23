import datetime

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from Database import Database
from logger import alert, logger

LOGGER = logger('WhatsApp')
WEB_WHATSAPP_URL = "https://web.whatsapp.com/"


class WhatsApp:
    def __init__(self, index=None, admin=None, profile_id=None):
        self.admin = admin
        self.profile_id = profile_id or Database().profile_ids[index]
        self.index = index
        LOGGER.info(f'{self.admin} instanced')
        mla_url = 'http://127.0.0.1:35000/api/v1/profile/start?automation=true&profileId=' + self.profile_id
        self.resp = requests.get(mla_url).json()
        if self.resp['status'] == 'OK':
            value = self.resp['value']
            self.driver = webdriver.Remote(command_executor=value, desired_capabilities={'acceptSslCerts': True})

    def authorisation(self):  # todo: more features
        self.driver.get(WEB_WHATSAPP_URL)
        LOGGER.info(f'{self.admin} Whatsapp загружается')
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.execute_script('return document.readyState;') == 'complete')
            WebDriverWait(self.driver, 60).until(
                lambda d: 'Не отключайте свой телефон' in self.driver.page_source)
            return True
        except TimeoutException:
            LOGGER.warning(f'{self.admin} Убедитесь, что ваш телефон подключен к Интернету.')
            alert(f'{self.admin} Убедитесь, что ваш телефон подключен к Интернету.')
            return False

    def spam(self):
        targets = Database().targets[self.index].split('\n')
        message = Database().messages[self.index]
        if type(message) is float:
            return False
        LOGGER.info(f'{self.admin} спам запущен')
        alert(f'{self.admin} спам запущен')
        for target in targets:
            try:
                search_bar = '//*[@id="side"]/div[1]/div/label/div/div[2]'
                search_bar_element = WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, search_bar))
                search_bar_element.clear()
                print(self.admin, target)
                search_bar_element.send_keys(target)
                group_xpath = f'//span[@title="{target}"]'
                WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, group_xpath))
                self.driver.find_element(By.XPATH, group_xpath).click()
                text_area = '//*[@id="main"]/footer/div[1]/div[2]/div/div[1]/div/div[2]'
                text_area_element = WebDriverWait(self.driver, 7).until(
                    lambda d: self.driver.find_element(By.XPATH, text_area))
                text_area_element.clear()
                for line in (message).splitlines():
                    if str.encode(line[:-1]) != b'\n':
                        text_area_element.send_keys(line)
                    text_area_element.send_keys(Keys.ALT + Keys.ENTER)
                text_area_element.send_keys(Keys.ENTER)
                print(f'{self.admin} сообщение отправлено')
            except TimeoutException as error:
                print('TimeoutException')
                continue
            except Exception as error:
                LOGGER.error(error, exc_info=True)
                continue
        timeout = 120
        time = datetime.datetime.now() + datetime.timedelta(minutes=timeout)  # todo: запись и сбор этих данных в базу
        LOGGER.info(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}')
        alert(f'Для {self.admin} спам запустится в {time.strftime("%H:%M")}')
