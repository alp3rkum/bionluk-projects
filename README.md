# melissima-selenium
Final Date: 27.04.2024

This project is my *second* Web automation project that I've worked on as a freelancer on Bionluk. This program simply scrapes the data from [www.melissima.com](https://shop.melissima.com.tr/) into an Excel file. It was made in Python and uses Selenium.

During its operation, this program scraped 26 brands and over 80 pages of products. Doing so took over *an hour* of time. Then the data was written into .csv files.

Since this application wasn't compiled, it had a module to check if Selenium package was installed, and another module that checked if a ChromeDriver was installed, so it could install & update the necessary packages for it to run without the user having to manually download ChromeDriver and pip install selenium. The main module (main.py), including comments, is about 180 lines, so it is a very small program apart from Selenium package and ChromeDriver.

## What Could Be Better Now?

If I took a similar project now, I would code this program as follows:

* **C# WebView2 (Python has a WebView library too so that could be useful)**: Compared to Selenium, WebView/WebView2 is an embeeded browser engine that is actually used by Edge and Chrome, so it is far more stable (for some reason Selenium *likes to be on spotlight at all times*, like if you minimize the browser it can crash)
* **Parallel Programming**: A good Web Scraping program is also *fast*. If you have six categories to scrape (which Melissima had, as far as I can remember), you can open six processes to co-scrape all of them.

Neverthless, this project taught me a bit more about Web scraping and .csv files.
