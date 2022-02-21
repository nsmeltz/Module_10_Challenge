# Import Splinter and BeautifulSoup
from email.errors import HeaderMissingRequiredValue
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere": mars_hemeispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# 1. Mars Nasa News Site Article Scraping 

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # define parent element
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# 2. Jet Propulsion Labratory's Images Scraping

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with Beautiful Soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# 3. Mars Facts Table Scrape

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' from Pandas to scrape the entire table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index to the description column
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemeispheres(browser):
    # 1. Use Splinter browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # HTML object
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Retrieve all elements that contain image information
    images = img_soup.find_all('div', class_='item')
    i = 0

    # Iterate through each book
    for image in images:
        hemisphere = {}

        # Scrape Title
        title = image.find("h3").text.strip()
        hemisphere['title']= title

        # Click link to page with full resolution image
        browser.find_by_css('h3')[i].click()

        # Scrape url for full resolution image
        sample = browser.links.find_by_partial_text('Sample')
        image_url = sample[0]['href']
        hemisphere['image_url']= image_url

        # Add scraped data to list of dictionaries
        hemisphere_image_urls.append(hemisphere)

        #click the back button to scrape next image
        browser.back()

        i = i + 1
    
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())




