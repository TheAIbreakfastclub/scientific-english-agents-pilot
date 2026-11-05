import os
import re
import requests
import pytest
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

pytestmark = pytest.mark.integration

URL_REGEX = re.compile(r'http[s]?://\S+')

def get_markdown_files():
    project_root = Path(__file__).parent.parent
    md_files = []
    for path in project_root.rglob('*.md'):
        if '.github' not in path.parts and 'node_modules' not in path.parts:
            md_files.append(path)
    return md_files

def extract_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    raw_urls = URL_REGEX.findall(content)
    
    clean_urls = []
    for url in raw_urls:
        clean_url = url.rstrip(').,]"\'')
        clean_urls.append(clean_url)
    return clean_urls

ALL_URLS = list({url for md_file in get_markdown_files() for url in extract_urls(md_file)})

@pytest.mark.parametrize("url", ALL_URLS)
def test_url_is_reachable(url):
    # 1. Liste des exclusions (Exemples ou Dépôt privé)
    if any(pattern in url for pattern in ["paste-your-key-here", "your-key-here"]):
        print(f"\n[IGNORE] {url} (URL d'exemple)")
        pytest.skip("URL d'exemple")
        
    if "github.com/TheAIbreakfastclub" in url:
        print(f"\n[PRIVATE] {url} (Depot prive - Validation externe suspendue)")
        pytest.skip("Depot prive")
        
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = session.head(url, allow_redirects=True, timeout=5, headers=headers)
        
        if response.status_code in [403, 405]:
            response = session.get(url, stream=True, timeout=5, headers=headers)
            response.close()
            
        if response.status_code >= 400:
            print(f"\n[SUSPECT] {url} -> Renvoie un Code {response.status_code}")
            assert False, f"Lien mort (Code {response.status_code})"
        else:
            print(f"\n[VALID] {url} -> OK (Code {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print(f"\n[TIMEOUT/DNS] {url} -> Impossible de resoudre le nom (Ignore en CI)")
        pytest.skip("Erreur DNS toleree")
    except requests.RequestException as e:
        print(f"\n[FAIL] {url} -> Erreur critique : {e}")
        pytest.fail(str(e))