# commerce

Deployed on https://commerce-joselws.herokuapp.com/

## About

In this project, you can:

- Create an account (passwords are hashed, so don't worry, we also don't prompt for email)
- Login or logout anytime you wish
- Post items by a starting price and an optional image if you wish
    - **Important**: For the time being, the app only accepts jpg, jpeg, and png image formats no longer than 2mb, otherwise it won't work. I had to do it that way because Heroku might complain since it's a free account.
- Bid on other users items
- Comment on other user items
- Edit your item
- Delete your item
- Add or remove items from your watchlist
- Filter items by categories, or browse the most recent or most popular ones. You may also browse your posted items or your watchlist
- Close the auction on your item, letting the highest bid on it and its user win the auction.

### Pending features (to do list):

- rename my_items to user_items
- user username click redirect to user_items
- category name click redirect to category_page 
- signals testing
- secret key safekeeping within project
- heroku branch
    - default image
    - remove unnecessary signals
    - keep postgres credentials safe

### Possible feature ideas for the future:

- move to django forms
- speed up tests
- default image declared on Item model for single default image file
- split into multiple apps (add app_name to urls.py files and change the links to include the app name)
- newest view (sorted by created_at)
- search by price
- item search bar
- pagination
- delete bid
- edit comment
- delete comment 
- user panel for profile config
- admin panel customization
- turn it into a Fullstack Single Page Application with full-fledged features if someone is willing to pay for it **wink**