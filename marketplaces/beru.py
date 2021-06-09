import common.parser as parser
import unicodedata


class Beru(parser.Parser):
    APP_CODE = "ru.beru.android"

    def open(self, **kwargs):
        super(Beru, self).close(self.APP_CODE)
        super(Beru, self).open(self.APP_CODE)
        parser.Helpers.randomDelay()

    def close(self, **kwargs):
        super(Beru, self).close(self.APP_CODE)

    def catalog(self, catalog_name):

        def find():
            if not self.d(text=catalog_name).exists:
                self.d(scrollable=True).scroll.forward()
                find()
            else:
                self.d(text=catalog_name).click()

        find()

        parser.Helpers.randomDelay()

    def parseCatalog(self):
        # Дождемся пока результаты появятся
        results = self.d(resourceId="ru.beru.android:id/searchResultListView")

        results.scroll.toBeginning(steps=10, max_swipes=99999)
        results.wait(timeout=5.0)

        already = []
        data = []

        scrolling = True
        scrolling_start = False

        while scrolling:
            if scrolling_start:
                print("Scrolling forward")
                make_scroll = results.scroll.forward()

                # Если скроллить ниже не получается - делаем еще одну попытку
                # Дело в том, что новые элементы списка могли не успеть подгрузиться по сети
                if make_scroll:
                    print("Scrolling okay")
                    scrolling = make_scroll
                else:
                    print("Scrolling forward failed, trying one more time in 2 seconds")
                    parser.Helpers.randomDelay()
                    scrolling = results.scroll.forward()

            scrolling_start = True

            for elem in self.d.xpath(
                    "//*[@resource-id='ru.beru.android:id/searchResultListView']//*[@resource-id='ru.beru.android:id/productOfferTitleView']").all():

                if elem.text in already:
                    pass
                    print("Name " + elem.text + " duplicated! Skipping...")
                else:
                    print("Found name with data // " + elem.text)
                    already.append(elem.text)

                    elem.click()

                    product = {}

                    product_title = self.d(resourceId="ru.beru.android:id/productSummaryTitleView")
                    product_price = self.d(resourceId="ru.beru.android:id/actualPriceView")
                    product_old_price = self.d(resourceId="ru.beru.android:id/basePriceView")
                    product_brand = self.d(resourceId="ru.beru.android:id/button", instance=0)
                    product_reviews = self.d(resourceId="ru.beru.android:id/ratingBriefView", instance=0)

                    if product_title.exists:
                        product_title.wait()
                        product['title'] = product_title.get_text()

                    if product_price.exists:
                        price = product_price.get_text()
                        product['price'] = unicodedata.normalize("NFKD", price)

                    if product_old_price.exists:
                        old_price = product_old_price.get_text()
                        product['old_price'] = unicodedata.normalize("NFKD", old_price)

                    if product_brand.exists:
                        product['brand'] = product_brand.get_text()

                    if product_reviews.exists:
                        product['reviews'] = product_reviews.get_text()

                    data.append(product)

                    print(product)

                    self.d.press('back')
                    self.d(resourceId="ru.beru.android:id/searchResultListView").wait()

        print(data)

    def clickCatalog(self, and_wait=True):
        self.d(resourceId="ru.beru.android:id/nav_catalog", instance=0).click()

        if and_wait:
            parser.Helpers.randomDelay()
