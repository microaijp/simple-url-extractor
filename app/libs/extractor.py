from bs4 import BeautifulSoup, Comment, CData
from trafilatura import extract as trafilatura_extract
import chardet
import httpx
import json

async def getHTML(url: str) -> str:
    """
    Fetches the HTML content of a given URL.

    Args:
        url (str): The URL to fetch the HTML content from.

    Returns:
        str: The HTML content of the URL.

    Raises:
        httpx.RequestError: If there is an error making the HTTP request.
        Exception: If there is any other error during the process.
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", 
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
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
        
        extract_result = trafilatura_extract(html, output_format='json',
                                url=url, include_images=False, with_metadata=True)
        
        extract_data = json.loads(extract_result)
        
        extract_data["source_hostname"] = extract_data["source-hostname"]
        del extract_data["source-hostname"]
        
        await saveCache(url, extract_data)
        return extract_data
    
    except Exception as e:
        raise e
    
    