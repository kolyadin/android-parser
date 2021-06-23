import marketplaces.beru

if __name__ == '__main__':
    # Выполни adb devices в консоли, чтобы узнать идентификатор устройства
    d = marketplaces.beru.Beru('R58R5306C6Z')
    d.open()
    d.clickCatalog()
    d.catalog('Продукты питания')
    d.catalog('Чай, кофе, какао')
    d.catalog('Кофе')
    d.catalog('Молотый кофе')

    d.parseCatalog()
    d.close()

    exit(0)
