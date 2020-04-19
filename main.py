import scrapy
import time
import requests
import os
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from twisted.internet import task
from scrapy.crawler import CrawlerRunner
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)
CRAWLER_INTERVAL = 300  # in seconds
CHAT_ID = os.getenv('CHAT_ID')  # Telegram chat id (or user id)


class XboxStorePriceCrawler(scrapy.Spider):
    name = 'xboxstorespider'
    allowed_domains = ['microsoft.com']
    start_urls = [
        'https://www.microsoft.com/pt-BR/p/call-of-duty-modern-warfare-edicao-digital-padrao/9nvqbq3f6w9w?activetab=pivot:overviewtab'
    ]

    def parse(self, response):
        for price in response.css('#ProductPrice_productPrice_PriceContainer'):
            price_text = price.css('.pi-price-text>span::text').extract_first()
            get_price = price_text.split("R$")[1]
            format_send_price(
                get_price.split(',')[0],
                'https://www.microsoft.com/pt-BR/p/call-of-duty-modern-warfare-edicao-digital-padrao/9nvqbq3f6w9w?activetab=pivot:overviewtab'
            )
            yield {"price": price_text}


class BuscapeZoomPriceCrawler(scrapy.Spider):
    name = 'buscapespider'
    allowed_domains = ['buscape.com.br', 'zoom.com.br']
    start_urls = [
        'https://www.buscape.com.br/jogos-xbox-one/jogo-call-of-duty-modern-warfare-xbox-one-activision',
        'https://www.zoom.com.br/jogos-xbox-one/jogo-call-of-duty-modern-warfare-xbox-one-activision'
    ]

    def parse(self, response):
        for offer in response.css('.offers-list__offer'):
            price = offer.css('.price__total::text').extract_first()
            link = offer.css('.zbtn.zbtn--cpc::attr(href)').extract_first()
            format_send_price(price[2:], link)
            yield {"price": price}


def format_send_price(price, link):
    formated_price = int(price)
    t = time.localtime()
    if formated_price < 200:
        text = "Preço do Call Of Duty baixou! \n\n Valor: {} \n\n Horário: {} \n\n {}".format(
            price,
            time.strftime("%H:%H:%S", t),
            link,
        )
        send_message(text, CHAT_ID)


def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def run():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BuscapeZoomPriceCrawler)
    process.start(stop_after_crawl=False)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def run_crawl():
    runner = CrawlerRunner({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })
    runner.crawl(XboxStorePriceCrawler)
    runner.crawl(BuscapeZoomPriceCrawler)
    CrawlerRunner()


def start():
    send_message("Seu BOT iniciou!", CHAT_ID)
    l = task.LoopingCall(run_crawl)
    # Time in seconds to run next crawler + notification
    l.start(CRAWLER_INTERVAL)
    print("Running...")
    reactor.run()


if __name__ == "__main__":
    start()
