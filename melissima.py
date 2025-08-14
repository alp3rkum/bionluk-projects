from checkpackages import check_package
from checkdriver import check_chromedriver
###Gerekli paketlerin yüklü olup olmadığını kontrol eder, değilse yükler
check_package("selenium")


###Google Chromedriver sürümünü kontrol eder
check_chromedriver()

###Gerekli paketleri (yüklendikten sonra) import eder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

MARKALAR_EXISTS = False
URUN_EXISTS = False

page_url = 'https://shop.melissima.com.tr/'
marka_file_path = r"files/markalar.csv"
urun_file_path = r"files/urunler.csv"
if not os.path.exists(marka_file_path):
    print("Markalar CSV dosyası bulunamadı. Oluşturuluyor...")
    os.makedirs(os.path.dirname(marka_file_path),exist_ok=True)

    marka_file = open(marka_file_path,'w+')
    if not "marka,markalogo\n" in marka_file:
        marka_file.write("marka,markalogo\n")
        marka_file.close()
else:
    print("Markalar dosyası bulundu!")
    MARKALAR_EXISTS = True

if not os.path.exists(urun_file_path):
    print("Ürünler CSV dosyası bulunamadı. Oluşturuluyor...")
    os.makedirs(os.path.dirname(urun_file_path),exist_ok=True)

    urun_file = open(urun_file_path,'w+')
    if not "stok_kodu,urun_adi,urun_aciklama,urun_foto1,urun_foto2,urun_foto3,urun_foto4,kategori,urun_marka,urun_fiyat\n" in urun_file:
        urun_file.write("stok_kodu,urun_adi,urun_aciklama,urun_foto1,urun_foto2,urun_foto3,urun_foto4,kategori,urun_marka,urun_fiyat\n")
else:
    print("Ürünler dosyası bulundu!")
    URUN_EXISTS = True

time.sleep(1)    

browser = webdriver.Chrome()

browser.get(page_url)
browser.implicitly_wait(10)

###Marka logolarını getirir
def logos():
    while True:
        existing_brand_count = 0 
        marka_file = open(marka_file_path,'a+')
        logolar = browser.find_element(By.CLASS_NAME,"owl-stage").find_elements(By.XPATH,"./*[self::div]")
        if(logolar):
            for logo in logolar:
                if(logo.find_element(By.TAG_NAME,"li").find_element(By.TAG_NAME,"a").find_element(By.TAG_NAME,"img").get_attribute("src") != "https://static.ticimax.cloud/53520/uploads/images/load.gif"):
                    marka = logo.find_element(By.TAG_NAME,"li").find_element(By.TAG_NAME,"a").find_element(By.TAG_NAME,"img").get_attribute("alt")
                    marka_logo = logo.find_element(By.TAG_NAME,"li").find_element(By.TAG_NAME,"a").find_element(By.TAG_NAME,"img").get_attribute("src")
                    line_exists = False
                    marka_file.seek(0)
                    for line in marka_file:
                        if f"{marka},{marka_logo}\n" in line:
                            line_exists = True
                            existing_brand_count += 1
                    if not line_exists:
                        marka_file.write(f"{marka},{marka_logo}\n")
        marka_file.close()
        if existing_brand_count == len(logolar)-4:
            break
        time.sleep(2.5)

def products():
    category_link_List = []
    print("Ürün kategorileri kazınıyor...")
    categories = browser.find_elements(By.CLASS_NAME,"ulVar")
    if categories:
        for category in categories:
            print(category.find_element(By.TAG_NAME,"a").get_attribute("href"))
            category_link_List.append(category.find_element(By.TAG_NAME,"a").get_attribute("href"))
        for category_link in category_link_List[:-1]:
            browser.get(category_link + "?sayfa=1")
            time.sleep(1)
            page_number = 1
            while browser.current_url == category_link + f"?sayfa={page_number}":
                product_list = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID,"ProductPageProductList")))
                # product_list = browser.find_element(By.ID,"ProductPageProductList")
                if(product_list):
                    print("Ürün listesini buldum!")
                    # product_links_element = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"productName")))
                    product_links_element = product_list.find_elements(By.CLASS_NAME,"productName")
                    product_links = [link_element.find_element(By.TAG_NAME,"a").get_attribute("href") for link_element in product_links_element]
                    for link in product_links:
                        time.sleep(0.5)
                        print(link)
                        browser.get(link)
                        
                        data_row = ""

                        stock_code = browser.execute_script("return productDetailModel.stockCode;")
                        if stock_code:
                            data_row += stock_code + "||"
                        product_name = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME,"ProductName")))
                        if(product_name):
                            data_row += product_name.text + "||"
                        product_description = browser.find_element(By.CSS_SELECTOR,'.urunTabAlt').text
                        if(product_description):
                            data_row += product_description.split('\n')[0] + "||"
                        images_div = browser.find_element(By.CLASS_NAME,"SmallImages")
                        if(images_div):
                            images = images_div.find_elements(By.TAG_NAME,"img")
                            if(images):
                                images_count = 0
                                for image in images:
                                    data_row += image.get_attribute("src") + "||"
                                    images_count += 1
                                if images_count < 4:
                                    for i in range(4-images_count):
                                        data_row += "none||"
                        product_category = ""
                        product_category_list = browser.find_element(By.CLASS_NAME,"breadcrumb").find_elements(By.TAG_NAME,"li")
                        if(product_category_list):
                            for category_level in product_category_list[1:-1]:
                                if category_level != product_category_list[-2]:
                                    product_category += category_level.find_element(By.TAG_NAME,"a").text + " > "
                                else:
                                    product_category += category_level.find_element(By.TAG_NAME,"a").text
                            # product_category = f"{product_category_list[1].find_element(By.TAG_NAME,'a').text} > {product_category_list[2].find_element(By.TAG_NAME,'a').text} > {product_category_list[3].find_element(By.TAG_NAME,'a').text}"
                            if product_category:
                                data_row += product_category + "||"
                        product_brand = browser.find_element(By.CLASS_NAME,"t2").find_element(By.TAG_NAME,"span").text
                        if(product_brand):
                            data_row += product_brand + "||"
                        product_price = browser.find_element(By.CLASS_NAME,"spanFiyat").text
                        if(product_price):
                            data_row += product_price
                        else:
                            data_row += "1"
                        
                        print(data_row)

                        line_exists = False
                        urun_file = open(urun_file_path,'a+', encoding="utf-8")
                        urun_file.seek(0)
                        urun_file.readline()
                        for line in urun_file:
                            if data_row.replace("₺","") + "\n" in line:
                                line_exists = True
                        if not line_exists:
                            urun_file.write(data_row.replace("₺","") + "\n")
                        urun_file.close()

                page_number += 1
                browser.get(category_link + f"?sayfa={page_number}")
                time.sleep(1)
                # product_links = [link.find_element(By.TAG_NAME,"a").get_attribute("href") for link in product_links_element]
                # for product_link in product_links:
                #     print(product_link)
                #     print(type(product_link))
                #     browser.get(product_link)
                #     time.sleep(1)
                    
                        

def main():
    marka_file = open(marka_file_path,'r')
    marka_file.seek(0)
    if not MARKALAR_EXISTS:
        print("Markalar CSV dosyası bulunamadı. Logoları getiriliyor...")
        logos()
    products()

main()