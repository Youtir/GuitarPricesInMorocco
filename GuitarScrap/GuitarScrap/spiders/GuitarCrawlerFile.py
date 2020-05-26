import scrapy
import csv
import pymysql.cursors

class GuitarCrawlerClass(scrapy.Spider):
    name = 'GuitarCrawler'
    start_urls = ['https://rock.ma/fr/7-guitares-electriques']

    def parse(self, response):
        yield scrapy.Request('https://rock.ma/fr/17-guitares-classiques', callback=self.parsepage, cb_kwargs=dict(guitarcategory='guitares-classiques'))
        categorypages = response.css('ul.category-sub-menu li')
        for brutpage in categorypages:
            categorypage = brutpage.css('a::attr(href)').get()
            categorypage = response.urljoin(categorypage)
            yield scrapy.Request(categorypage, callback=self.parsepage)



    def parsepage(self, response):
        productpages = response.css('div.product-description h2')
        for page in productpages:
            category = response.url.split('/')[-1]
            productpage = page.css('a::attr(href)').get()
            productpage = response.urljoin(productpage)
            yield scrapy.Request(productpage, callback=self.parseproduct, cb_kwargs=dict(guitarcategory=category))

    def parseproduct(self, response, guitarcategory):
        productname = response.css('div.col-md-6 h1::text').get()
        productprice = response.css('div.current-price span::text').get()

        connection = pymysql.connect(host='localhost', user='root', password='', db='scrapydb', )

        #Saving Data in a MySQL Database
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO guitars (name, category, price) VALUES (%s, %s , %s)"
                cursor.execute(sql, (productname, guitarcategory, productprice))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
        finally:
            connection.close()

        #Second Option saving data as csv
        '''with open('products.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([productname, guitarcategory, productprice])'''

