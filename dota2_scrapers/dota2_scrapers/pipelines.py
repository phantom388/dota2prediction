from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
from scrapy.conf import settings

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class Dota2ScrapersPipeline(object):
    def process_item(self, item, spider):
        return item

class DatDotaCsvItemPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open('%s.csv' % spider.name, 'w+b')
        self.files[spider.name] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = [
            'match_id',
            'radiant_team',
            'dire_team',
            'winner',
            'radiant_player_0',
            'radiant_player_1',
            'radiant_player_2',
            'radiant_player_3',
            'radiant_player_4',
            'radiant_hero_0',
            'radiant_hero_1',
            'radiant_hero_2',
            'radiant_hero_3',
            'radiant_hero_4',
            'dire_player_0',
            'dire_player_1',
            'dire_player_2',
            'dire_player_3',
            'dire_player_4',
            'dire_hero_0',
            'dire_hero_1',
            'dire_hero_2',
            'dire_hero_3',
            'dire_hero_4'
            ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider.name)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

def item_type(item):
    return type(item).__name__.lower()

class DotabuffCsvItemPipeline(object):

    def __init__(self):
        self.item_types = ['hero', 'player']

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.files = dict([(item_type, open('%s_%s.csv' % (spider.name, item_type), 'w+b')) for item_type in self.item_types])
        self.exporters = dict([(item_type, CsvItemExporter(self.files[item_type])) for item_type in self.item_types])
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        t = item_type(item)
        if t in self.item_types:
            self.exporters[t].export_item(item)
        return item
