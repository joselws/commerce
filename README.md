# commerce
Third project for "Web Programming with Python and JavaScript" course 2020 on edX by CS50 - HarvardX.

This project is an E-commerce site, in which users can post listings to open auctions and where other users can bid on it.

Login, register and logout logic were provided by the course staff.

In this project, I showcased the use of Django and Django ORM to accomplish the following tasks:

- Create normalized data models for the application.
- Let user create listings with name, description, starting price, image URL, etc.
- Home page that shows latest active listings.
- A view page for each listing in which users can see details on the listing, make bids, and post comments.
- - All bids made on the listing must be greater than the current highest bid
- Ability to open and close existing listings by their creators. The winner of the bid is showed when the listing is closed.
- Implement a 'watchlist' feature in which users can add the listings they want to their watchlist list. Moreover, a page that renders all listings in their watchlist is also implemented.
- Create a category page in which all listing categories are listed. By clicking in each of them, the user is presented with all listings pertaining to the selected category.
- Edit Django Admin for easy edition of the site models (To be implemented).
