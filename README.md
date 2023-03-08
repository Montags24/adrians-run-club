# Adrian's Run Club

## Aim
As a keen runner, I am always looking out for deals on new shoes, especially ones used for racing as they wear out quite quickly. The main site I use to look up deals is RunRepeat, which allows you to filter by shoe, size and type (trail, road, track etc). The site however doesn't alert you to deals, so it is down to you to go onto the site regularly to see if the shoe is on sale. 

Adrian's Run Club will scrape the website RunRepeat for its competitive shoes and store the data in a database. The site will allow users to select shoes and sizes to get email alerts when they go on sale. This is my first attempt at a full-stack app.

## Technologies used:
- Bootstrap v5.0 to create the front-end of the web using HTML and CSS
- Python v3.11 with the Flask framework for the back-end
- SQLite for storing data in a database, SQLalchemy to query the database
- Git for version control
- Selenium and Beautiful Soup to scrape data from RunRepeat





## Problems faced and lessons learned
### Web scraping
- Having built a web scraper using Beautiful Soup and Selenium, I was able to parse through the HTML on RunRepeat to get the data that I wanted, shoe name, price, discount, link to the image and link to the deal if on sale. However, after consulting the robots.txt extension, I found out that many of the pages that I wanted to scrape were disallowed by the site. This led me to wonder if the site was using an API to retrieve its data. By using Chrome's developer tools, and looking at the requests the site was making, I was able to figure out that they were using an API, and passing through specific numbers as filters based on the shoes size, use (road, trail, track etc.), whether the shoe is used for daily use/competition and so on. This I found to be much faster and more reliable than webscraping, so I incorprated their API into the design of my app. 
### Relationship mapping within database
- Got stuck on this for hours. My database is made up of two sheets. The first sheet (Brand) contains all the names of the shoes, whilst the second (Shoe) contains all the information about the shoe (size, price, discount, image link, deal link). By having the Brand sheet at as the parent and the Shoe sheet as the child, I would be able to relate shoe data to the name of the shoe. Using SQLalchemy, to create a table sheet you base it off a Class, in this case I had a Brand and Shoe class. To relate the Shoe and Brand class, I included a foreign key. I thought I could link the shoe class to the brand class by name, eg "Nike" but actually needed to link it via its primary key.
- Getting the shoe data to import into the database was a real HOORAH moment.

