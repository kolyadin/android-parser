import marketplaces.beru

if __name__ == '__main__':
    # Выполни adb devices в консоли, чтобы узнать идентификатор устройства
    d = marketplaces.beru.Beru('UGPN9D5PA6NV49UO')
    d.open()
    d.clickCatalog()
    d.catalog('Электроника')
    d.catalog('Смартфоны и аксессуары')
    d.catalog('Рации и прочие телефоны')
    d.catalog('Проводные телефоны')

    d.parseCatalog()
    d.close()

    exit(0)
