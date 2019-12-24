import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

# import gevent
# from gevent import monkey
# monkey.patch_all()
import requests
from lxml import etree
import re
from twitter_video_downloader.twitter_dl import TwitterDownloader

def count_time(fun):
    def warpper(*args):
        s_time = time.time()
        fun(*args)
        e_time = time.time()
        t_time = e_time - s_time
        print('%s耗时：%s' % (fun.__name__, t_time))
    return warpper


class Twitter():
    def __init__(self):
        self.proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'https://127.0.0.1:1080',
        }
        self.orgin_file = r'124419.txt'
        self.user = 'Ding1204'
        self.follow_dir='follow'

    def get_twitter(self, file):
        pic_t_list = []
        with open(file, encoding='utf8') as f:
            t_list = f.readlines()
            for twitter in t_list:
                res = re.match('.*(pic.twitter.com.*)', twitter)
                if res:
                    pic_t_list.append(res.group(1))
        pic_t_list = ['https://' + pic_t for pic_t in pic_t_list]
        # print(pic_t_list)
        return pic_t_list

    def get_pics_url(self, url):
        page_source = requests.get(url, timeout=10, proxies=self.proxies).content
        selector = etree.HTML(page_source)
        # print('url:%s,page_source:%s'%(url,page_source))
        # pic_urls=selector.xpath('//div[@class="AdaptiveMedia-quadPhoto"]//img/@src')
        pic_urls = selector.xpath(
            '//div[@class="permalink-inner permalink-tweet-container"]//img[starts-with(@src,"https://pbs.twimg.com/media")]/@src')
        # pic_urls=selector.xpath('//div[@class="AdaptiveMedia-quadPhoto"]//img/@src')
        # print('pic_urls:%s'%pic_urls)
        # is_video=selector.xpath('//video[@preload="none"]/@src')

        return pic_urls

    def downloadpic(self, url, path):
        name = url.split('/')[-1]
        file_path = os.path.join(path, name)
        if os.path.exists(file_path):
            print('已下载:%s' % file_path)
        pic_content = requests.get(url, timeout=10, proxies=self.proxies).content
        with open(file_path, 'wb') as f:
            f.write(pic_content)
            print(file_path)

    def download(self, pic_t, path):
        # print('download:%s' % pic_t)
        pic_urls = self.get_pics_url(pic_t)
        # for pic_url in pic_urls:
        #     self.downloadpic(pic_url, path)

        # if not pic_urls:
        res = requests.get(pic_t, proxies=self.proxies)
        print(res.url)
        twitter_dl = TwitterDownloader(res.url, output_dir=path)
        twitter_dl.download()

    def count_pic(self):
        l = os.listdir('download_twitter')
        print('图片数量:%d' % len(l))

    @count_time
    def main(self):
        follow_list = os.listdir(self.follow_dir)
        for follow in follow_list:
            print('download user:%s'%follow)
            path = os.path.join('download_twitter', follow.split('.')[0])
            if not os.path.exists(path):
                os.makedirs(path)
            pic_t_list = self.get_twitter(os.path.join(self.follow_dir, follow))
            print('pic_t_list:%s' % len(pic_t_list))

            #thead pool
            # t_list = []
            # with ThreadPoolExecutor() as executor:
            #     for pic_t in pic_t_list:
            #         obj = executor.submit(self.download, pic_t, path)
            #         t_list.append(obj)
            #     as_completed(t_list)

            #single thread
            for pic_t in pic_t_list:
                self.download(pic_t,path)


            self.count_pic()


if __name__ == '__main__':
    t = Twitter()
    t.main()
