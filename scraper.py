from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import requests
import time
import random

def run_mal_scraper(pages):
	"""Run MAL scraper on top anime/manga characters

	Args:
		pages (int): How many pages to search through (50 characters per page)

	Returns:
		List of JSON objects containing character name and anime name.
	"""
	c_list = []
	for i in range(0, pages*page_size, page_size):
		soup = get_bs4_soup(f'https://myanimelist.net/character.php?limit={i}')
		if soup:
			ranking_table = soup.find_all('tr', class_='ranking-list')

			for row in ranking_table:
				name = get_character_name(row)
				anime_name = get_anime_name(row)
				img_link = get_image_search(row)
				if name and anime_name and img_link:
					c_list.append({'c_name': name.text, 'a_name': anime_name.text, 'img_link': img_link['data-src']})

		else:
			print(f'Error conducting for overall ranking scrape')
			return c_list # Return early, likely 403, should add more explicit error handling
	return c_list

# Add random delay to reduce frequency of 403 errors aka bot detection on MAL
def rand_delay():
	# sleep_min and sleep_max are in seconds
	sleep_min = 2
	sleep_max = 4
	time.sleep(random.uniform(sleep_min, sleep_max))

def get_bs4_soup(url):
	rand_delay()
	try:
		user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) ' \
             'Gecko/20071127 Firefox/2.0.0.11'
		hdr = {'User-Agent': user_agent}
		req = Request(url, headers=hdr)
		page = urlopen(req)
		if page.status == requests.codes.ok:
			html = page.read().decode("utf-8")
			soup = BeautifulSoup(html, "html.parser")
		else:
			return None
		return soup
	except Exception as e:
		# TODO: Add error propagation
		print(f'Encountered error...')
		print(f'Error: {e}')
		return None

def get_character_name(bs_item):
	name_list = bs_item.find_all('a', class_='fs14 fw-b')
	name = name_list[0] if name_list and len(name_list) > 0 else None
	return name

def get_anime_name(bs_item):
	animeography_list = bs_item.find_all('td', class_='animeography')
	title_list = animeography_list[0].find_all('div', class_='title') if animeography_list and len(animeography_list) > 0 else None
	anime_name_list = title_list[0].find_all('a') if title_list and len(title_list) > 0 else None
	anime_name = anime_name_list[0] if anime_name_list and len(anime_name_list) > 0 else None
	return anime_name

def get_image_search(bs_item):
	name_list = bs_item.find_all('a', class_='fs14 fw-b', href=True)
	name = name_list[0] if name_list and len(name_list) > 0 else None
	character_page = name['href'] if name else None
	if character_page:
		soup = get_bs4_soup(character_page)
		if soup:
			sidebar = soup.find_all('td', class_='borderClass')
			if sidebar:
				img = sidebar[0].find_all('img')
				if img:
					return img[0]
		else:
			print(f'Error conducting image search')
	return None


if __name__ == '__main__':
	page_size = 50;
	c_list = run_mal_scraper(1)
	print(len(c_list))
	# for x in c_list:
	# 	print(x)