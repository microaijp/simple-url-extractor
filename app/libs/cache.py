import json
import os
import time
import hashlib

CACHE_DIR = "../cache"


def hash_text(text: str, algorithm: str = 'sha256') -> str:
    """
    テキストを指定したハッシュアルゴリズムでハッシュ化する

    Parameters:
    text (str): ハッシュ化するテキスト
    algorithm (str): 使用するハッシュアルゴリズム（デフォルトは 'sha256'）

    Returns:
    str: ハッシュ化されたテキスト
    """
    # 使用するハッシュアルゴリズムを取得
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(text.encode('utf-8'))
    return hash_func.hexdigest()

async def saveCache(cache_key: any, data: any):
    """
    save cache
    """
    if not isinstance(cache_key, str):
        cache_key = json.dumps(cache_key)

    cache_key = hash_text(cache_key)
    cache_file_name = f"{cache_key}.json"
    cache_data = {
        "time": int(time.time()),
        "data": data
    }
    
    cache_file_path = os.path.join(CACHE_DIR, cache_file_name)
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file_path, "w") as f:
        json.dump(cache_data, f)
    



async def getCache(cache_key: any, cache_seconds: int = 60):
    """
    get cache
    """
    if not isinstance(cache_key, str):
        cache_key = json.dumps(cache_key)


    cache_key = hash_text(cache_key)
    cache_file_name = f"{cache_key}.json"
    cache_file_path = os.path.join(CACHE_DIR, cache_file_name)
    
    cache_data = None
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as f:
            cache_data = json.load(f)
    else:
        return None
    
    if int(time.time()) - cache_data['time'] < cache_seconds:
        return cache_data['data']

    return None