import re

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}


def get_source_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the source by requests
    """
    proxies = {"http": proxy} if proxy is not None else None
    response = None
    try:
        with requests.Session() as session:
            if data:
                response = session.post(
                    url, headers=headers, data=data, proxies=proxies, timeout=timeout
                )
            else:
                response = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
        
        # ========== 编码修复（使用 requests 自带的 apparent_encoding）==========
        # 自动检测真实编码
        detected_encoding = response.apparent_encoding
        print(f"🔍 自动检测到编码: {detected_encoding} for {url}")
        
        # 用检测到的编码重新解码
        raw_content = response.content
        try:
            fixed_text = raw_content.decode(detected_encoding)
        except (UnicodeDecodeError, LookupError):
            # 失败则回退到 utf-8
            print(f"⚠️ 解码失败，回退到 utf-8 for {url}")
            fixed_text = raw_content.decode('utf-8', errors='ignore')
        
        # 替换 response 的 text 属性
        response._text = fixed_text
        response.encoding = detected_encoding if detected_encoding else 'utf-8'
        # ========== 修复结束 ==========
        
    except requests.RequestException:
        return ""
    source = re.sub(
        r"<!--.*?-->",
        "",
        response.text if response is not None else "",
        flags=re.DOTALL,
    )
    return source


def get_soup_requests(url, data=None, proxy=None, timeout=30):
    """
    Get the soup by requests
    """
    source = get_source_requests(url, data, proxy, timeout)
    soup = BeautifulSoup(source, "html.parser")
    return soup
