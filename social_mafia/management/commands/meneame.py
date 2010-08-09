import logging
import random
import re
import urllib2

from lxml.html import fromstring


POSITIVE_MENEO = re.compile('^(?P<user>.+):.*(?P<when>\d{2}:\d{2})\sUTC\svalor:\s+(?P<value>\d+)')
NEGATIVE_MENEO = re.compile('^(?P<user>.+):.*(?P<when>\d{2}:\d{2})\sUTC$')

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.4) Gecko/20100611 Firefox/3.6.4',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-us; rv:1.8.1.5) Gecko/20080221 Firefox/3.3.1',
    'Mozilla/5.0 (Macintosh; U; Baltix Linux; lt; rv:1.9.2.2) Gecko/20100215 Firefox/3.6.1',
]

logging.basicConfig(level=logging.DEBUG)


def get_page(url):
    opener = urllib2.build_opener()
    user_agent = random.choice(USER_AGENTS)
    logging.debug('get_page: %s, User-Agent: %s' % (url, user_agent))

    opener.addheaders = [
        ('User-agent', user_agent),
    ]
    f = opener.open(url)
    return fromstring(f.read())


def get_article_votes(article_id, pages):
    votes = []
    for page in range(1, pages + 1):
        r = get_page("http://www.meneame.net/backend/meneos.php?id=%d&p=%d" % (article_id, page))
        for a in r.xpath("//div[@class='item']/a"):
            title_text = unicode(a.attrib['title']).encode('utf8', 'ignore')
            title_text = title_text.replace('\xc2\xa0', ' ')
            m = POSITIVE_MENEO.match(title_text)
            if m:
                data = m.groupdict()
                data['value'] = int(data['value'])
                votes.append(data)
            else:
                # didn't match, this is a negative meneo
                m = NEGATIVE_MENEO.match(title_text)
                if m:
                    data = m.groupdict()
                    data['value'] = -1
                    votes.append(data)
                else:
                    raise ValueError('ERROR: %r' % title_text)

    return votes


def get_article_id(root):
    text = root.xpath("//div[@class='mnm-published']/a/@id")
    return int(text[0].split('-')[2])


def get_number_pages(url):
    votes_url = url + '/voters'
    root = get_page(votes_url)

    last = root.xpath("//div[@class='mini-pages']/a[last()]")
    return int(last[0].text)


def get_article_stats(url):
    root = get_page(url)

    article_id = get_article_id(root)
    pages = get_number_pages(url)
    votes = get_article_votes(article_id, pages)

    return {
        'id': article_id,
        'votes': votes,
    }


def get_articles(pages=0):
    base_url = 'http://www.meneame.net/?page=%d'
    if not pages:
        # no limits man
        root = get_page(base_url % 1)
        last = root.xpath("//div[@class='pages-margin']/a[last() - 1]/text()")
        pages = int(last[0])

    for i in xrange(1, pages):
        root = get_page(base_url % i)
        for url in root.xpath("//div[@class='mnm-published']/a/@href"):
            yield url


if __name__ == '__main__':
    for url in get_articles():
        print url
