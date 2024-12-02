from bs4 import BeautifulSoup, Comment, CData
from trafilatura import extract as trafilatura_extract
import chardet
import httpx
import json
import re
from fake_useragent import UserAgent
import asyncio
import random
from http.cookies import SimpleCookie
from bs4 import UnicodeDammit
import logging
from typing import Optional, Tuple
import backoff

logger = logging.getLogger(__name__)

class RequestManager:
    def __init__(self):
        self.ua = UserAgent()
        self.retry_delay = 2
        self.max_retries = 3

    def get_headers(self) -> dict:
        """Generate browser-like headers with rotating User-Agent"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "no-cache"
        }

async def handle_bot_protection(response: httpx.Response) -> bool:
    """Handle various bot protection mechanisms"""
    content = await response.aread()
    text = content.decode('utf-8', errors='ignore')

    # Incapsula対策
    if 'Incapsula' in text:
        cookies = SimpleCookie()
        if 'set-cookie' in response.headers:
            cookies.load(response.headers['set-cookie'])
            # クッキーの処理をここで行う
        await asyncio.sleep(random.uniform(2, 4))
        return True

    # Cloudflare対策
    if 'cf-browser-verification' in text:
        await asyncio.sleep(random.uniform(3, 5))
        return True

    return False

def detect_encoding(content: bytes, content_type: str) -> str:
    """
    Detect the character encoding of the content using multiple methods
    """
    encoding = None

    # 1. Content-Typeヘッダーからの検出
    if content_type and 'charset=' in content_type.lower():
        encoding = content_type.lower().split('charset=')[-1].strip()

    # 2. HTMLメタタグからの検出
    if not encoding:
        try:
            head = content[:1024].decode('ascii', errors='ignore')
            if 'charset=' in head.lower():
                encoding = head.lower().split('charset=')[-1].split('"')[0].split('\'')[0].strip()
        except Exception:
            pass

    # 3. chardetによる検出
    if not encoding:
        detected = chardet.detect(content)
        encoding = detected['encoding']

    # 4. UnicodeDammitによる検出
    if not encoding:
        dammit = UnicodeDammit(content)
        encoding = dammit.original_encoding

    # 5. フォールバック
    if not encoding:
        encoding = 'utf-8'

    return encoding

@backoff.on_exception(
    backoff.expo,
    (httpx.RequestError, asyncio.TimeoutError),
    max_tries=3,
    max_time=30
)
async def getHTML(url: str) -> str:
    """
    Enhanced HTML fetching with bot protection and robust character encoding handling
    """
    request_manager = RequestManager()
    
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ) as client:
        try:
            response = await client.get(
                url,
                headers=request_manager.get_headers()
            )
            response.raise_for_status()

            # BOT対策の処理
            if await handle_bot_protection(response):
                # 必要に応じて再リクエスト
                response = await client.get(url, headers=request_manager.get_headers())
                response.raise_for_status()

            # レート制限への対応
            if response.status_code in [429, 503]:
                retry_after = int(response.headers.get('Retry-After', request_manager.retry_delay))
                await asyncio.sleep(retry_after)
                response = await client.get(url, headers=request_manager.get_headers())
                response.raise_for_status()

            # 文字コードの検出と変換
            content_type = response.headers.get('content-type', '')
            encoding = detect_encoding(response.content, content_type)

            # UnicodeDammitを使用した堅牢なデコード
            dammit = UnicodeDammit(response.content, override_encodings=[encoding] if encoding else None)
            html = dammit.unicode_markup

            if not html:
                # フォールバックデコード
                try:
                    html = response.content.decode(encoding, errors='replace')
                except Exception:
                    html = response.content.decode('utf-8', errors='replace')

            return html

        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise
        except Exception as e:
            logger.err

async def cleanUpHtml(html: str):
    """
    Cleans up the HTML by removing unwanted elements and attributes.

    Args:
        html (str): The HTML string to be cleaned up.

    Returns:
        str: The cleaned up HTML string.

    Raises:
        Exception: If an error occurs during the cleaning process.
    """
    
    try:
        # remove unwanted elements and attributes
        soup = BeautifulSoup(html, 'html.parser')
        
        # remove comments and cdata
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        
        # remove cdata
        cdatas = soup.findAll(text=lambda text:isinstance(text, CData))
        for cdata in cdatas:
            cdata.extract()
        
        # remove unwanted tags
        tags_to_remove = ['script', 'style', 'nav', 'footer', 'aside', 'form', 'iframe']
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()
        
        # remove unwanted attributes
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            script.decompose()
        
        # remove style attributes
        for tag in soup.find_all(True):
            if 'style' in tag.attrs:
                del tag.attrs['style']
        
        return str(soup)
    
    except Exception as e:
        raise e

def make_absolute_urls(html_content, base_url):
    from lxml import html
    from urllib.parse import urljoin
    tree = html.fromstring(html_content)
    
    for elem in tree.xpath('//*[@href or @src or @data-src]'):
        if elem.tag == 'a':
            href = elem.get('href')
            if href and not href.startswith(('http://', 'https://')):
                elem.set('href', urljoin(base_url, href))
        elif elem.tag == 'img':
            src = elem.get('src')
            data_src = elem.get('data-src')
            if src and not src.startswith(('http://', 'https://')):
                elem.set('src', urljoin(base_url, src))
            if data_src and not data_src.startswith(('http://', 'https://')):
                elem.set('data-src', urljoin(base_url, data_src))
    
    return html.tostring(tree, encoding='unicode')


async def extract(url: str, cache_seconds: int = 600):
    """
    Extracts information from a given URL.

    Args:
        url (str): The URL to extract information from.
        cache_seconds (int, optional): The number of seconds to cache the extracted information. Defaults to 600.

    Returns:
        dict: A dictionary containing the extracted information.

    Raises:
        Exception: If there is an error during the extraction process.
    """
    
    from libs.cache import getCache, saveCache
    
    # check cache
    cache = await getCache(url, cache_seconds)
    if cache:
        return cache
    
    try:
        # get html
        html = await getHTML(url)
        if not html:
            raise Exception("HTML is empty")

        # clean up html
        html = await cleanUpHtml(html)
        
        # absolute urls
        html = make_absolute_urls(html, url)
        html = html.replace('figure', 'p')
        
        # extract_result = trafilatura_extract(html, output_format='json',
        #                         url=url, include_images=True, with_metadata=True, include_links=True)
        
        # alt属性とsrc属性の順序に関係なくキャプチャする正規表現
        img_tag_regex = r'<img[^>]*(?:alt="([^"]*)")?[^>]*src="([^"]+)"[^>]*>|<img[^>]*src="([^"]+)"[^>]*(?:alt="([^"]*)")?[^>]*>'

        def replace_img_tags(match):
            alt = match.group(1) if match.group(1) else match.group(4)
            src = match.group(2) if match.group(2) else match.group(3)
            alt_text = alt if alt else '画像'
            return f'111222333000-{src}-000333222111'
            # return f'これは本文です。[{alt_text}]({src})'

        # alt属性がある場合を処理
        html = re.sub(img_tag_regex, replace_img_tags, html)

        extract_result = trafilatura_extract(html, output_format='json',
                                include_images=True, with_metadata=True, include_links=True, favor_precision=True, url=url)
        
        
        if extract_result == None:
            raise Exception("No data extracted")
        
        extract_data = json.loads(extract_result)
        
        extract_data["text"] = extract_data["text"].replace('111222333000-', '').replace('-000333222111', '')
        extract_data["raw_text"] = extract_data["raw_text"].replace('111222333000-', '').replace('-000333222111', '')
        
        extract_data["source_hostname"] = extract_data["source-hostname"]
        del extract_data["source-hostname"]
        
        await saveCache(url, extract_data)
        return extract_data
    
    except Exception as e:
        raise e
    
    
