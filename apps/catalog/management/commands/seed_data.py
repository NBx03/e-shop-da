import io
import os
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.catalog.models import Category, Product, ProductStatus, PreorderRequest

def generate_placeholder_webp(title: str, category_name: str, color_hex: str) -> ContentFile:
    """
    Generates a clean, modern placeholder image in WebP format
    """
    width, height = 600, 600
    img = Image.new('RGB', (width, height), color=color_hex)
    draw = ImageDraw.Draw(img)

    # Draw stylish background card
    margin = 30
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline='#FFFFFF',
        width=3
    )

    # Draw label text
    # In Pillow, default font is always available
    text = f"{title}\n\n[{category_name}]"
    draw.text((width // 2, height // 2), text, fill='#FFFFFF', anchor="mm")

    output = io.BytesIO()
    img.save(output, format='WEBP', quality=85)
    output.seek(0)
    safe_name = title.lower().replace(' ', '_').replace('/', '_')[:25]
    return ContentFile(output.read(), name=f"{safe_name}.webp")


class Command(BaseCommand):
    help = "Наполняет базу данных 25 реалистичными товарами электроники в 5 разделах"

    def handle(self, *args, **options):
        self.stdout.write("Очистка или обновление каталога...")

        categories_data = [
            {'name': 'Смартфоны', 'slug': 'smartphones', 'icon': 'smartphone', 'color': '#2563EB'},
            {'name': 'Ноутбуки', 'slug': 'laptops', 'icon': 'laptop', 'color': '#059669'},
            {'name': 'Наушники и аудио', 'slug': 'audio', 'icon': 'headphones', 'color': '#7C3AED'},
            {'name': 'Планшеты', 'slug': 'tablets', 'icon': 'tablet', 'color': '#D97706'},
            {'name': 'Умный дом', 'slug': 'smarthome', 'icon': 'home', 'color': '#DC2626'},
        ]

        cat_objs = {}
        for idx, c in enumerate(categories_data):
            cat, _ = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'icon': c['icon'], 'order': idx, 'is_active': True}
            )
            cat_objs[c['slug']] = (cat, c['color'])

        sample_products = [
            # Смартфоны
            {
                'category': 'smartphones',
                'title': 'Apple iPhone 15 Pro Max 256GB',
                'slug': 'iphone-15-pro-max',
                'price': Decimal('134990.00'),
                'old_price': Decimal('149990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Флагманский смартфон Apple с титановым корпусом, процессором A17 Pro и передовой системой камер с 5x оптическим зумом.',
                'specs': {'Процессор': 'Apple A17 Pro', 'Память': '256 ГБ', 'Экран': '6.7" OLED 120Hz', 'Цвет': 'Natural Titanium'}
            },
            {
                'category': 'smartphones',
                'title': 'Samsung Galaxy S24 Ultra 512GB',
                'slug': 'samsung-s24-ultra',
                'price': Decimal('129990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Интеллектуальный флагман с функциями Galaxy AI, встроенным пером S Pen и 200 Мп камерой для ночной съемки.',
                'specs': {'Процессор': 'Snapdragon 8 Gen 3', 'Память': '512 ГБ', 'Экран': '6.8" Dynamic AMOLED 2X', 'Цвет': 'Titanium Gray'}
            },
            {
                'category': 'smartphones',
                'title': 'Xiaomi 14 Pro 12/256GB',
                'slug': 'xiaomi-14-pro',
                'price': Decimal('79990.00'),
                'old_price': Decimal('89990.00'),
                'status': ProductStatus.ON_THE_WAY,
                'description': 'Оптика Leica Summilux, новый процессор Snapdragon и ультрабыстрая зарядка HyperCharge 120 Вт.',
                'specs': {'Процессор': 'Snapdragon 8 Gen 3', 'Память': '12/256 ГБ', 'Оптика': 'Leica', 'Цвет': 'Black'}
            },
            {
                'category': 'smartphones',
                'title': 'Google Pixel 8 Pro 128GB',
                'slug': 'google-pixel-8-pro',
                'price': Decimal('84990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Чистый Android с поддержкой 7 лет обновлений, процессор Google Tensor G3 и лучшие алгоритмы вычислительной фотографии.',
                'specs': {'Процессор': 'Google Tensor G3', 'Память': '128 ГБ', 'Экран': '6.7" Super Actua', 'Цвет': 'Bay Blue'}
            },
            {
                'category': 'smartphones',
                'title': 'Nothing Phone (2) 12/256GB',
                'slug': 'nothing-phone-2',
                'price': Decimal('56990.00'),
                'old_price': Decimal('62990.00'),
                'status': ProductStatus.PREORDER,
                'description': 'Уникальный прозрачный дизайн с интерфейсом глифов, самобытная оболочка Nothing OS 2.0 и отличная автономность.',
                'specs': {'Процессор': 'Snapdragon 8+ Gen 1', 'Память': '12/256 ГБ', 'Глифы': 'LED подсветка', 'Цвет': 'Dark Grey'}
            },

            # Ноутбуки
            {
                'category': 'laptops',
                'title': 'Apple MacBook Pro 16 M3 Pro 18/512GB',
                'slug': 'macbook-pro-16-m3',
                'price': Decimal('249990.00'),
                'old_price': Decimal('269990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Профессиональный ноутбук с невероятной автономностью до 22 часов, экраном Liquid Retina XDR и чипом M3 Pro.',
                'specs': {'Чип': 'Apple M3 Pro', 'ОЗУ': '18 ГБ', 'SSD': '512 ГБ', 'Экран': '16.2" Liquid Retina XDR 120Hz'}
            },
            {
                'category': 'laptops',
                'title': 'Apple MacBook Air 13 M2 8/256GB',
                'slug': 'macbook-air-m2',
                'price': Decimal('99990.00'),
                'old_price': Decimal('109990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Тонкий и легкий ультрабук весом 1.24 кг без вентиляторов — бесшумная работа при любой нагрузке.',
                'specs': {'Чип': 'Apple M2', 'ОЗУ': '8 ГБ', 'SSD': '256 ГБ', 'Вес': '1.24 кг', 'Цвет': 'Midnight'}
            },
            {
                'category': 'laptops',
                'title': 'ASUS ROG Zephyrus G16 (RTX 4070)',
                'slug': 'asus-rog-zephyrus-g16',
                'price': Decimal('219990.00'),
                'old_price': None,
                'status': ProductStatus.ON_THE_WAY,
                'description': 'Игровой ноутбук в тонком алюминиевом корпусе с OLED экраном 240 Гц и мощной видеокартой RTX 4070.',
                'specs': {'CPU': 'Intel Core Ultra 9', 'GPU': 'RTX 4070 8GB', 'ОЗУ': '32 ГБ', 'SSD': '1 ТБ'}
            },
            {
                'category': 'laptops',
                'title': 'Lenovo ThinkPad X1 Carbon Gen 11',
                'slug': 'lenovo-thinkpad-x1',
                'price': Decimal('179990.00'),
                'old_price': Decimal('195000.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Эталон корпоративного ноутбука: прочный корпус из углеродного волокна, легендарная клавиатура и надежная защита.',
                'specs': {'CPU': 'Intel Core i7-1365U', 'ОЗУ': '16 ГБ', 'SSD': '512 ГБ', 'Вес': '1.12 кг'}
            },
            {
                'category': 'laptops',
                'title': 'Framework Laptop 16 (Modular)',
                'slug': 'framework-laptop-16',
                'price': Decimal('189990.00'),
                'old_price': None,
                'status': ProductStatus.PREORDER,
                'description': 'Полностью модульный ноутбук с возможностью апгрейда любых компонентов: видеокарты, портов и материнской платы.',
                'specs': {'CPU': 'AMD Ryzen 7 7840HS', 'Модульность': '100% апгрейд', 'ОЗУ': '32 ГБ', 'SSD': '1 ТБ'}
            },

            # Наушники и аудио
            {
                'category': 'audio',
                'title': 'Sony WH-1000XM5 Wireless Noise Cancelling',
                'slug': 'sony-wh1000xm5',
                'price': Decimal('36990.00'),
                'old_price': Decimal('42990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Лидер в активном шумоподавлении с двумя процессорами и 8 микрофонами, поддержка Hi-Res Audio LDAC.',
                'specs': {'Тип': 'Полноразмерные', 'Шумоподавление': 'ANC (8 микрофонов)', 'Автономность': 'до 30 ч'}
            },
            {
                'category': 'audio',
                'title': 'Apple AirPods Pro 2 (USB-C)',
                'slug': 'airpods-pro-2-usbc',
                'price': Decimal('23990.00'),
                'old_price': Decimal('26990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Флагманские TWS наушники с адаптивным аудио, чипом H2 и обновленным кейсом с портом USB-C.',
                'specs': {'Чип': 'Apple H2', 'Зарядка': 'USB-C / MagSafe', 'Защита': 'IP54'}
            },
            {
                'category': 'audio',
                'title': 'Marshall Major IV Bluetooth',
                'slug': 'marshall-major-iv',
                'price': Decimal('14990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Культовый рок-дизайн, беспроводная зарядка и более 80 часов непрерывного воспроизведения музыки.',
                'specs': {'Автономность': '80+ часов', 'Динамики': '40 мм', 'Вес': '165 г'}
            },
            {
                'category': 'audio',
                'title': 'Bose QuietComfort Ultra Headphones',
                'slug': 'bose-qc-ultra',
                'price': Decimal('44990.00'),
                'old_price': Decimal('49990.00'),
                'status': ProductStatus.ON_THE_WAY,
                'description': 'Пространственное аудио Bose Immersive Audio и непревзойденный комфорт для многочасовых перелетов.',
                'specs': {'Звук': 'Bose Immersive Audio', 'Автономность': '24 ч', 'Цвет': 'White Smoke'}
            },
            {
                'category': 'audio',
                'title': 'Sennheiser HE 1 Orpheus (Exclusive)',
                'slug': 'sennheiser-he-1',
                'price': Decimal('4990000.00'),
                'old_price': None,
                'status': ProductStatus.PREORDER,
                'description': 'Лучшая в мире электростатическая система для аудиофилов с усилителем в корпусе из каррарского мрамора.',
                'specs': {'Класс': 'Ultra High-End', 'Корпус': 'Каррарский мрамор', 'Диапазон': '8 Гц — 100 кГц'}
            },

            # Планшеты
            {
                'category': 'tablets',
                'title': 'Apple iPad Pro 13 M4 256GB Wi-Fi',
                'slug': 'ipad-pro-13-m4',
                'price': Decimal('149990.00'),
                'old_price': Decimal('164990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Революционный Ultra Retina XDR Tandem OLED дисплей толщиной всего 5.1 мм на мощнейшем чипе Apple M4.',
                'specs': {'Чип': 'Apple M4', 'Экран': '13" Tandem OLED', 'Толщина': '5.1 мм', 'Цвет': 'Space Black'}
            },
            {
                'category': 'tablets',
                'title': 'Apple iPad Air 11 M2 128GB',
                'slug': 'ipad-air-11-m2',
                'price': Decimal('69990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Универсальный планшет для учебы, творчества и работы с поддержкой стилуса Apple Pencil Pro.',
                'specs': {'Чип': 'Apple M2', 'Память': '128 ГБ', 'Экран': '11" Liquid Retina'}
            },
            {
                'category': 'tablets',
                'title': 'Samsung Galaxy Tab S9 Ultra 512GB',
                'slug': 'samsung-tab-s9-ultra',
                'price': Decimal('109990.00'),
                'old_price': Decimal('124990.00'),
                'status': ProductStatus.ON_THE_WAY,
                'description': 'Огромный 14.6" Dynamic AMOLED 2X экран с защитой от воды IP68 и пером S Pen в комплекте.',
                'specs': {'Экран': '14.6" AMOLED 120Hz', 'Защита': 'IP68', 'ОЗУ': '12 ГБ', 'S Pen': 'В комплекте'}
            },
            {
                'category': 'tablets',
                'title': 'Xiaomi Pad 6 8/256GB',
                'slug': 'xiaomi-pad-6',
                'price': Decimal('32990.00'),
                'old_price': Decimal('36990.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Сбалансированный планшет с экраном 144 Гц, 4 динамиками Dolby Atmos и процессором Snapdragon 870.',
                'specs': {'Экран': '11" 2.8K 144Hz', 'Батарея': '8840 мАч', 'Звук': '4 динамика Dolby Atmos'}
            },
            {
                'category': 'tablets',
                'title': 'Remarkable 2 Digital Paper Tablet',
                'slug': 'remarkable-2',
                'price': Decimal('54990.00'),
                'old_price': None,
                'status': ProductStatus.PREORDER,
                'description': 'Планшет с экраном CANVAS, имитирующим тактильные ощущения письма на настоящей бумаге. Без отвлекающих уведомлений.',
                'specs': {'Экран': '10.3" E-Ink CANVAS', 'Толщина': '4.7 мм', 'Автономность': 'до 2 недель'}
            },

            # Умный дом
            {
                'category': 'smarthome',
                'title': 'Яндекс Станция Дуо Макс с Алисой',
                'slug': 'yandex-station-duo-max',
                'price': Decimal('42990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Первая умная колонка Яндекса с поворотным сенсорным экраном, хабом управления Zigbee и мощным звуком 60 Вт.',
                'specs': {'Экран': '10.5" поворотный', 'Звук': '60 Вт', 'Протокол': 'Zigbee 3.0 / Wi-Fi'}
            },
            {
                'category': 'smarthome',
                'title': 'Робот-пылесос Roborock S8 Pro Ultra',
                'slug': 'roborock-s8-pro-ultra',
                'price': Decimal('119990.00'),
                'old_price': Decimal('135000.00'),
                'status': ProductStatus.IN_STOCK,
                'description': 'Флагманская станция самоочистки, ультразвуковая влажная уборка VibraRise 2.0 и всасывание 6000 Па.',
                'specs': {'Мощность': '6000 Па', 'Станция': 'Сушка + стирка + очистка', 'Навигация': '3D LiDAR'}
            },
            {
                'category': 'smarthome',
                'title': 'Apple TV 4K Wi-Fi + Ethernet 128GB',
                'slug': 'apple-tv-4k-128gb',
                'price': Decimal('18990.00'),
                'old_price': None,
                'status': ProductStatus.IN_STOCK,
                'description': 'Медиаплеер с поддержкой Dolby Vision, HDR10+, чипом A15 Bionic и протоколом Thread для умного дома.',
                'specs': {'Чип': 'Apple A15 Bionic', 'Память': '128 ГБ', 'Поддержка': 'Thread / Matter / Gigabit LAN'}
            },
            {
                'category': 'smarthome',
                'title': 'Умный увлажнитель Smartmi Evaporative Humidifier 3',
                'slug': 'smartmi-humidifier-3',
                'price': Decimal('11990.00'),
                'old_price': Decimal('13990.00'),
                'status': ProductStatus.ON_THE_WAY,
                'description': 'Естественное традиционное увлажнение без белого налета и ультразвука. Резервуар 5 л, тихая ночная работа.',
                'specs': {'Расход': '350 мл/ч', 'Бак': '5 литров', 'Управление': 'Приложение / Алиса'}
            },
            {
                'category': 'smarthome',
                'title': 'Cyberdog 2 Companion Robot',
                'slug': 'xiaomi-cyberdog-2',
                'price': Decimal('399990.00'),
                'old_price': None,
                'status': ProductStatus.PREORDER,
                'description': 'Бионический робот-собака нового поколения с искусственным интеллектом, 19 датчиками и динамической балансировкой.',
                'specs': {'Датчики': '19 сенсоров (LiDAR + камеры)', 'ИИ': '21 TOPS AI чип', 'Вес': '8.9 кг'}
            },
        ]

        created_count = 0
        for item in sample_products:
            cat, color = cat_objs[item['category']]
            prod, created = Product.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'category': cat,
                    'title': item['title'],
                    'price': item['price'],
                    'old_price': item['old_price'],
                    'status': item['status'],
                    'description': item['description'],
                    'characteristics': item['specs'],
                    'is_active': True,
                }
            )

            # Generate WebP image if product has no image
            if not prod.main_image:
                webp_img = generate_placeholder_webp(prod.title, cat.name, color)
                prod.main_image.save(f"{prod.slug}.webp", webp_img, save=True)

            if created:
                created_count += 1

        # Seed sample preorder requests so admin looks realistic!
        preorder_prods = Product.objects.filter(status=ProductStatus.PREORDER)
        sample_preorders = [
            ('Алексей Смирнов', '+7 999 123-45-67', 12345678),
            ('Дмитрий Кузнецов', '+7 916 555-88-99', 87654321),
            ('Елена Попова', '+7 903 777-33-22', None),
        ]
        for idx, (name, phone, tg_id) in enumerate(sample_preorders):
            if preorder_prods.exists():
                prod = preorder_prods[idx % preorder_prods.count()]
                PreorderRequest.objects.get_or_create(
                    product=prod,
                    customer_phone=phone,
                    defaults={'customer_name': name, 'telegram_user_id': tg_id}
                )

        self.stdout.write(self.style.SUCCESS(
            f"Успешно загружено {len(sample_products)} товаров в {len(categories_data)} разделах! "
            f"Создано заявок «Хочу такой»: {len(sample_preorders)}."
        ))
