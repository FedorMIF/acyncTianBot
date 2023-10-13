from selenium import webdriver
from selenium.webdriver.common.by import By

# Настройка драйвера
driver = webdriver.Chrome('/path/to/chromedriver')

# Открыть веб-страницу
driver.get('https://topmemas.top')

# Найти все элементы img на странице
img_elements = driver.find_elements(By.TAG_NAME, 'img')

# Извлечь ссылки на изображения
img_links = [img.get_attribute('src') for img in img_elements]

# Вывести все найденные ссылки
for link in img_links:
    print(link)

# Закрыть браузер
driver.quit()