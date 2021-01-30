from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests
import time
import random
import sys
import traceback

PAGE_SIZE = 50
TOP_N_CHARACTERS = 30000

exc_info = sys.exc_info()

def run_mal_scraper(pages, char_per_page = PAGE_SIZE):
	"""Run MAL scraper on top anime/manga characters

	Args:
		pages (int): How many pages to search through (50 characters per page)
		char_per_page (int): How many characters from each page to store

	Returns:
		List of JSON objects containing character name and anime name.
	"""
	c_list = []
	for i in range(0, pages*PAGE_SIZE, PAGE_SIZE):
		try:
			soup = get_bs4_soup(f'https://myanimelist.net/character.php?limit={i}')
			ranking_table = soup.find_all('tr', class_='ranking-list')

			counter = 0
			for row in ranking_table:
				if counter == char_per_page:
					break
				name = get_character_name(row)
				anime_name = get_anime_name(row)
				img_link = get_image_search(row)
				rank = get_rank(row)
				if name and anime_name and img_link:
					v_rank = rank.text
					v_name = name.text
					v_anime_name = anime_name.text
					v_img_link = img_link["data-src"]
					# item = {'c_name': name.text, 'a_name': anime_name.text, 'img_link': img_link['data-src']}
					character_str = f'{v_rank} | {v_name} | {v_anime_name} | {v_img_link}'
					# print(item)
					# c_list.append(item)
					file.write(f'{character_str}\n')
				counter += 1
		except Exception as e:
			raise e.with_traceback(sys.exc_info()[2])
	return c_list

def remove_special_chars(s):
	# Some URLs have special characters, which we should ignore
	return s.encode('ascii', 'ignore').decode('ascii')

# Add random delay to reduce frequency of 403 errors aka bot detection on MAL
def rand_delay():
	# sleep_min and sleep_max are in seconds
	sleep_min = 1
	sleep_max = 4
	time.sleep(random.uniform(sleep_min, sleep_max))

def get_bs4_soup(url):
	rand_delay()
	try:
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) ' \
             'Gecko/20071127 Firefox/2.0.0.11'
		hdr = {'User-Agent': user_agent}
		req = Request(remove_special_chars(url), headers=hdr)
		page = urlopen(req)
		if page.status == requests.codes.ok:
			html = page.read().decode("utf-8")
			soup = BeautifulSoup(html, "html.parser")
			return soup
		else:
			print(f'Non-ok status code opening URL {req}')
			raise Exception('Non-ok status code response.').with_traceback(sys.exc_info()[2])
	except Exception as e:
		exc_info = sys.exc_info()
		print(f'Exception opening URL {url.encode}')
		raise e

def get_character_name(bs_item):
	name = bs_item.find('a', class_='fs14 fw-b') or None
	return name

def get_anime_name(bs_item):
	animeography = bs_item.find('td', class_='animeography') or None
	title = animeography.find('div', class_='title') if animeography else None
	anime_name = title.find('a') if title else None
	return anime_name

def get_image_search(bs_item):
	name = bs_item.find('a', class_='fs14 fw-b', href=True) or None
	character_page = name['href'] if name else None
	if character_page:
		try:
			soup = get_bs4_soup(character_page)
			sidebar = soup.find('td', class_='borderClass') if soup else None
			img = sidebar.find('img') if sidebar else None
			return img
		except Exception as e:
			raise e
	return None

def get_rank(bs_item):
	rank_container = bs_item.find('td', class_='rank') or None
	rank = rank_container.find('span') if rank_container else None
	return rank


if __name__ == '__main__':
	file = open('character_scrape.txt', 'a')
	try:
		c_list = run_mal_scraper(TOP_N_CHARACTERS//PAGE_SIZE)
	except Exception as e:
		traceback.print_exception(*exc_info)
		del exc_info
	finally:
		file.close()