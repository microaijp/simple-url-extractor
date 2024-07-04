from bs4 import BeautifulSoup, Comment, CData
from trafilatura import extract as trafilatura_extract
import chardet
import httpx
import json

async def getHTML(url: str) -> str:
    """
    指定されたURLからHTMLを取得する非同期関数
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", 
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        
        encoding = chardet.detect(response.content)['encoding']
        if encoding != "MacRoman":
            try:
                if encoding == "EUC-JP":
                    html = response.content.decode(encoding, 'ignore')
                elif encoding == "KOI8-R":
                    html = response.content.decode("Shift_JIS")
                elif encoding == "Windows-1254":
                    html = response.content.decode("utf-8")
                else:
                    html = response.content.decode(encoding)
            except Exception as e:
                html = response.content.decode(response.encoding, 'ignore')
        else:
            html = response.content.decode(response.encoding, 'ignore')
        
    except httpx.RequestError as e:
        raise e
    except Exception as e:
        raise e
    
    return html

async def cleanUpHtml(html: str):
    """
    HTMLからコメント、CDATA、不要なタグを削除する
    """
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # コメントを削除
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        
        # CDATAを削除
        cdatas = soup.findAll(text=lambda text:isinstance(text, CData))
        for cdata in cdatas:
            cdata.extract()
        
        # 不要なタグを削除
        tags_to_remove = ['script', 'style', 'nav', 'footer', 'aside', 'form', 'iframe']
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()
        
        # application/ld+jsonを削除
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            script.decompose()
            
        # 不要な属性を削除（例：style属性）
        for tag in soup.find_all(True):
            if 'style' in tag.attrs:
                del tag.attrs['style']
        
        return str(soup)
    
    except Exception as e:
        raise e
    
async def extract(url: str, cache_seconds: int = 600):
    """
    """
    
    from libs.cache import getCache, saveCache
    
    # check cache
    # cache = await getCache(url, cache_seconds)
    # if cache:
    #     return cache
    
    try:
        # get html
        html = await getHTML(url)
        if not html:
            raise Exception("HTML is empty")

        # clean up html
        # html = await cleanUpHtml(html)
        print(html)
        
        extract_result = trafilatura_extract(html, output_format='json',
                                url=url, include_images=False)
        
        print(extract_result)
        extract_data = json.loads(extract_result)
        await saveCache(url, extract_data)
        return {
            # "html": html,
            "extract_data": extract_data
        }
    
    except Exception as e:
        raise 
    
    