from __future__ import annotations

from urllib.parse import urlparse
import requests
from lxml import etree

import pickle
from hashlib import md5
from pathlib import Path

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
	  'AppleWebKit/537.36 (KHTML, like Gecko)'
	  'Chrome/106.0.0.0 Safari/537.36')


def get_response(url: str) -> requests.Response:
	uid, name = (urlparse(url).path.split('/')[1:-1])

	if not ('quizlet.com' in url and uid.isdigit()):
		raise ValueError(f'{url} does not point to a '
		                 'Quizlet study set')

	res_fname = md5((uid + name).encode('utf-8')).hexdigest()
	res_path = Path(res_fname + '.pkl')
	if res_path.is_file():
		return pickle.loads(res_path.read_bytes())

	r = requests.get(url, headers={'User-Agent': UA})
	r.raise_for_status()
    
	with res_path.open('wb') as f:
		pickle.dump(r, f)
        
	return r


def get_cards(url: str) -> list[tuple[str, str]]:
	tree = etree.HTML(get_response(url).text)
	all_pairs = tree.xpath(
        '(//div[@class="SetPageTerm-inner"])[1]'
    )[0]
	terms = all_pairs.xpath(
        '//a[@class="SetPageTerm-wordText"]//text()'
    )
	defis = all_pairs.xpath(
	 '//a[@class="SetPageTerm-definitionText"]//text()'
    )
	return list(zip(terms, defis))
