import common.parser as parser
import unicodedata
from datetime import date, datetime
from uiautomator2.exceptions import UiObjectNotFoundError
import json
import codecs


class BadScrollException(Exception):
    """Исключение для ситуации, когда приложение виснет из-за бана"""
    pass


class Beru(parser.Parser):
    APP_CODE = "ru.beru.android"
    DEFAULT_TIMEOUT = 5
    PRODUCT_VIEW_XPATH = "//*[@resource-id='ru.beru.android:id/searchResultListView']//*[@resource-id='ru.beru.android:id/productOfferTitleView']"

    def _save_result(self):
        parsing_time_delta = self.ended - self.started
        result = {'items': self.items,
                  'parsingTime': int(parsing_time_delta.seconds * 1000 + parsing_time_delta.microseconds / 1000)}
        print(json.dumps(result, indent=4, ensure_ascii=False),
              file=codecs.open('output.json', 'w+', 'utf8'))

    def open(self, **kwargs):
        super(Beru, self).close(self.APP_CODE)
        super(Beru, self).open(self.APP_CODE)
        parser.Helpers.randomDelay()

    def close(self, **kwargs):
        super(Beru, self).close(self.APP_CODE)

    def _exit_product_view(self):
        # ожидаем, что вью, который можно скроллить, прогрузился
        self.d.press('back')
        self.d(resourceId="ru.beru.android:id/searchResultListView").wait()


    def _parse_product_view(self):
        product = {'market': 'beru', 'rank': self.rank,
                   'externalId': self.rank,
                   'category': 'Молотый кофе',
                   'observedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   'oldPrice': None,
                   'brand': None}

        product_title = self.d(
            resourceId="ru.beru.android:id/productSummaryTitleView")
        product_price = self.d(
            resourceId="ru.beru.android:id/pricesPriceView")
        product_old_price = self.d(
            resourceId="ru.beru.android:id/pricesBasePriceView")
        product_brand = self.d(
            resourceId="ru.beru.android:id/button", instance=0)

        if product_title.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
            title = product_title.get_text()
            product['title'] = product['sku'] = title
        else:
            product_title = self.d(resourceId="ru.beru.android:id/title")
            if product_title.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
                title = product_title.get_text()
                product['title'] = product['sku'] = title
            else:
                print('Product title not found')

        if product_price.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
            price = product_price.get_text()
            product['price'] = int(price.replace('\xa0', '').replace('₽', '') + '00')

        if product_old_price.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
            old_price = product_old_price.get_text()
            product['oldPrice'] = int(old_price.replace('\xa0', '').replace('₽', '') + '00')

        if product_brand.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
            brand = product_brand.get_text()
            if brand:
                product['brand'] = brand

        desc_rid = 'ru.beru.android:id/characteristicsAndDescriptionDescription'

        scroll_view = self.d(scrollable=True)
        if not scroll_view.wait(exists=True, timeout=2):
            return product
        
        if not scroll_view.scroll.to(resourceId=desc_rid):
            return product

        product_description = self.d(resourceId=desc_rid, instance=0)
        if not product_description.wait(exists=True, timeout=2):
            return product

        try:
            product_description.click(timeout=2)
        except UiObjectNotFoundError:
            return product

        product_description = self.d(resourceId=desc_rid, instance=0)
        if not product_description.wait(exists=True, timeout=self.DEFAULT_TIMEOUT):
            return product
        
        product['description'] = product_description.get_text()
        return product

    def _scroll_search_results(self):
        while not self.results.scroll.forward():
            parser.Helpers.randomDelay()
            self.scroll_view_retries -= 1
            if not self.scroll_view_retries:
                raise BadScrollException("Search results scrolling failed.")


    def catalog(self, catalog_name):

        def find():
            if not self.d(text=catalog_name).exists:
                self.d(scrollable=True).scroll.forward()
                find()
            else:
                self.d(text=catalog_name).click()

        find()

        parser.Helpers.randomDelay()

    def _restore_position(self):
        if not self.already:
            return
        # Скролллим до момента, пока не появляется новый товар
        results = self.d(resourceId="ru.beru.android:id/searchResultListView")

        results.scroll.toBeginning(steps=10, max_swipes=99999)
        results.wait(timeout=5.0)

        while True:
            for elem in self.d.xpath(self.PRODUCT_VIEW_XPATH).all():
                if elem.text not in self.already:
                    return True
            self._scroll_search_results()
    
    def _parse_scroll_view(self):
        self.results.wait(timeout=5.0)
        while True:
            self.scroll_view_retries = 8

            for elem in self.d.xpath(self.PRODUCT_VIEW_XPATH).all():
                # Скролл не всегда гарантирует появление нового элемента
                if elem.text in self.already:
                    pass
                else:
                    parser.Helpers.randomDelay()
                    self.already.add(elem.text)
                    self.rank += 1
                    elem.click()
                    product = self._parse_product_view()
                    self.ended = datetime.now()

                    if product:
                        self.items.append(product)
                        print(json.dumps(product, ensure_ascii=False))
                    parser.Helpers.randomDelay()
                    self._exit_product_view()
            self._scroll_search_results()
    
    def parseCatalog(self):
        """Точка входа в парсер."""
        self.results = self.d(resourceId="ru.beru.android:id/searchResultListView")
        self.results.scroll.toBeginning(steps=10, max_swipes=99999)
        self.results.wait(timeout=5.0)
        self.already = set()
        self.items = []
        self.rank = 0
        self.started = datetime.now()

        # количество попыток для детекции "бана"
        self.scroll_view_retries = 8

        self._parse_scroll_view()

    def clickCatalog(self, and_wait=True):
        self.d(resourceId="ru.beru.android:id/nav_catalog", instance=0).click()

        if and_wait:
            parser.Helpers.randomDelay()
