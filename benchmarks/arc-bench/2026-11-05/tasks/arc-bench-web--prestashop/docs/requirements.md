# PrestaShop B2C storefront

A B2C storefront for browsing products, selecting variants, managing a cart, completing checkout, and managing customer accounts.

Displayed dates use UTC and the shared application/evaluator clock 2026-10-06T12:00:00Z; elapsed time drives carousel behavior.

For verified customers: The scenarios use existing verified customer accounts; account verification is outside scope. Address books start empty; UI setup creates Home where required. The source historical-order account also owns completed delivered historical order. New customer email and profile-next email are initially unused. No initial account cart contains products.

For session, filters, selected combination, cart, checkout and recently viewed state: Produced through the corresponding user interactions. Do not inject storage, cookies or API state.

## REQ-1 Storefront discovery

Visitors discover the homepage and navigate through persistent global controls. Homepage content includes carousel promotions, popular product cards with quick view and wishlist controls, promotion area, newsletter and footer. Visual presentation follows homepage.png and navigation.png.

English action names are case-insensitive. Global navigation remains available across pages. Carousel active content is an image named for the current promotion; exactly one such image is visible.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Discover storefront content

Opening the storefront while logged out displays "Global navigation"(role=navigation), "Carousel"(role=region), "Popular Products"(role=region) containing Hummingbird detail t-shirt, "Promotions"(role=region), "Newsletter"(role=region), and the footer. Users navigate through "Logo"(role=link), "CLOTHES"(role=link), "Sign in"(role=button), and "Cart"(role=link), search with "Search"(role=searchbox), and access language selection through "Language"(role=combobox). Cart count starts at 0. All controls are keyboard-accessible, and mobile navigation collapses behind "Menu"(role=button).

English action names are case-insensitive. Global navigation remains available across pages.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Discover homepage
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** An anonymous visitor has an empty cart and the seeded catalog is available.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Open the storefront homepage.
    - **Then:** Global navigation, Carousel, Popular Products containing Hummingbird detail t-shirt, Promotions, Newsletter and footer are visible; Logo, CLOTHES, Sign in, Cart, Search and Language are available and Cart reports 0.
    - **References:** `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.1-02 — Use responsive keyboard navigation
  - **Step:** STEP-REQ-1.1-02-01
    - **Given:** The anonymous homepage is open with its desktop navigation visible.
    - **When:** Use Tab to reach each global navigation control; resize the viewport to 390×844, focus Menu and press Enter, then reach CLOTHES with Tab.
    - **Then:** Desktop controls are keyboard reachable; mobile Menu opens navigation and CLOTHES receives keyboard focus.
    - **References:** `\ref[image](IMG-HOMEPAGE)`

### REQ-1.2 Navigate categories and return home

Hovering or keyboard-focusing and activating "CLOTHES"(role=link) reveals "Men"(role=link) and "Women"(role=link). Men opens its product listing with Hummingbird detail t-shirt and Sort by; activating CLOTHES itself opens the parent category. From any catalog page, "Logo"(role=link) returns home to Popular Products.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-NAVIGATION · home**

![IMG-NAVIGATION · home](reference/navigation.png)

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.2-01 — Browse Men and return with logo
  - **Step:** STEP-REQ-1.2-01-01
    - **Given:** The anonymous homepage is open and the seeded catalog contains Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Hover CLOTHES, activate Men, then activate Logo.
    - **Then:** Men initially shows its heading, Sort by and Hummingbird detail t-shirt; Logo returns to the homepage with Popular Products.
    - **References:** `\ref[image](IMG-NAVIGATION)`, `\ref[image](IMG-CATEGORY)`
- SCN-REQ-1.2-02 — Open subcategory by keyboard
  - **Step:** STEP-REQ-1.2-02-01
    - **Given:** The anonymous homepage is open.
    - **When:** Focus CLOTHES using the keyboard, press Enter to reveal its submenu, then focus Men and press Enter.
    - **Then:** Men opens with its heading and Hummingbird detail t-shirt in Product list.
    - **References:** `\ref[image](IMG-NAVIGATION)`, `\ref[image](IMG-CATEGORY)`

### REQ-1.3 Search products

Focusing "Search"(role=searchbox) and entering shirt displays "Search suggestions"(role=region) with Hummingbird detail t-shirt. Pressing Enter submits the search and displays a "Product list"(role=region) containing that product.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-SEARCH · home**

![IMG-SEARCH · home](reference/search.png)

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.3-01 — Suggest and search shirt
  - **Step:** STEP-REQ-1.3-01-01
    - **Given:** The anonymous homepage is open and the catalog includes Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Fill Search (searchbox) with shirt, inspect Search suggestions, then press Enter in Search.
    - **Then:** Suggestions include Hummingbird detail t-shirt; the submitted Product list includes that same product.
    - **References:** `\ref[image](IMG-SEARCH)`, `\ref[image](IMG-CATEGORY)`

### REQ-1.4 Browse carousel promotions

"Carousel"(role=region) contains at least two visually distinct promotion slides. Its visible image source or accessible name changes automatically within five seconds; clicking "Next"(role=button) changes the slide immediately. "Shop now"(role=link) opens a product or category containing Hummingbird detail t-shirt.

The active carousel promotion is an image named for that promotion; exactly one promotion image is visible.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Displayed dates use UTC and the shared clock 2026-10-06T12:00:00Z; carousel transitions use elapsed time.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.4-01 — Advance automatically
  - **Step:** STEP-REQ-1.4-01-01
    - **Given:** The homepage Carousel is visible with an identifiable current promotion image.
    - **When:** Observe the carousel without activating a control for up to five seconds.
    - **Then:** The visible promotion image source or accessible name changes to a different slide.
    - **References:** `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.4-02 — Advance with Next
  - **Step:** STEP-REQ-1.4-02-01
    - **Given:** The homepage Carousel is visible and its current promotion is recorded.
    - **When:** Click Next (button) within Carousel.
    - **Then:** The visible promotion changes to a different slide.
    - **References:** `\ref[image](IMG-HOMEPAGE)`
- SCN-REQ-1.4-03 — Shop from promotion
  - **Step:** STEP-REQ-1.4-03-01
    - **Given:** The homepage Carousel offers Shop now (link).
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Activate Shop now.
    - **Then:** A product detail for Hummingbird detail t-shirt or a category containing that product opens.
    - **References:** `\ref[image](IMG-HOMEPAGE)`

### REQ-1.5 Open popular product

Within "Popular Products"(role=region), "Hummingbird detail t-shirt"(role=link) is keyboard-accessible. Activating it opens that same product's detail with its heading and Add to cart action.

Popular product cards include quick-view and wishlist controls.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.5-01 — Open popular t-shirt
  - **Step:** STEP-REQ-1.5-01-01
    - **Given:** The homepage Popular Products contains Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Reach its named product link using the keyboard and activate it.
    - **Then:** The product detail heading identifies Hummingbird detail t-shirt and Add to cart is visible.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-1.6 Open empty cart

With an empty visitor cart, clicking "Cart"(role=link) opens Shopping cart with an empty-cart message and no cart t-shirt row.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.6-01 — Inspect empty cart
  - **Step:** STEP-REQ-1.6-01-01
    - **Given:** An anonymous visitor has added no products and Cart shows 0.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Activate Cart (link) in Global navigation.
    - **Then:** Shopping cart displays an empty-cart message and no Hummingbird cart t-shirt row.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-CART)`

### REQ-1.7 Preview popular product without leaving home

Hovering "Product Hummingbird detail t-shirt"(role=region) within Popular Products reveals "Quick view"(role=button). Clicking it opens "Quick view Hummingbird detail t-shirt"(role=dialog) with that exact product and its current price 24. "Close"(role=button) dismisses the preview and restores the homepage's Popular Products without adding anything to the cart.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.7-01 — Preview popular product without leaving home
  - **Step:** STEP-REQ-1.7-01-01
    - **Given:** The anonymous homepage contains the popular Hummingbird detail t-shirt and an empty cart.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "review": {"text": "Good fit", "average_rating": 4}}
    - **When:** Hover its Product region, click Quick view (button), inspect the preview, then click Close within the dialog.
    - **Then:** Quick view Hummingbird detail t-shirt displays that product and price 24; Close dismisses it, Popular Products remains visible, and Cart still reports 0.
    - **References:** `\ref[requirement](REQ-1.5)`, `\ref[image](IMG-HOMEPAGE)`

## REQ-2 Catalog exploration

Visitors browse category, search and comparable listing contexts. Men provides breadcrumb, description, filters, product grid, count, sorting and pagination. Sidebar filters support availability, sale, category, size, color, composition, price and brand; concrete behavior is tested only where the source provides an oracle.

Product list contains one Product <name> region per product. Sale price contains just the current monetary amount and discounted cards also expose Regular price. Product count is a named status. Breadcrumb and Subcategories are named regions. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

For published catalog: Concrete representative values instantiate source constraints, not a database schema. All 13 products belong to Men, including the source Black mug. Source-named Hummingbird products and White t-shirt are on the first unfiltered page; order of other entries is unrestricted. Detail t-shirt has 20% discount (30 to 24), tax-inclusive price 24, tax-exclusive price 20, regular-fit description, reference HB-DETAIL, cotton data sheet, regular-fit features, at least two images, seeded review Good fit with average rating 4, and related Men products. Women listing is available. Additional representative combinations make the source dynamic-price/stock rule executable: default M/White costs 24 with stock 50; L/Black costs 36 with stock 2. Front and Back image assets must be visually distinct. The extra size/color combination does not change listing default prices or the 13-product Men pagination world.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Browse category hierarchy

The Men category displays its heading, "Category description"(role=region), numeric "Product count"(role=status), "Sort by"(role=combobox), and product grid. "Breadcrumb"(role=navigation) presents Home, CLOTHES, and Men in order; its "CLOTHES"(role=link) returns to the parent category with CLOTHES heading and a Men entry. Parent-category Men and "Women"(role=link) entries are keyboard-accessible, and Women opens its own listing with Sort by.

The category sidebar provides availability, sale, category, size, color, composition, price, and brand filters. Concrete behavior is specified only where the source provides an oracle. Subcategories is a named region.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.1-01 — Inspect category and breadcrumb
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** The seeded catalog is available to an anonymous visitor.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Open CLOTHES then Men through Global navigation.
    - **Then:** Men heading, Category description, numeric Product count, Sort by and Product list are visible; Breadcrumb presents Home, CLOTHES and Men in that order.
    - **References:** `\ref[image](IMG-CATEGORY)`
- SCN-REQ-2.1-02 — Return to parent category
  - **Step:** STEP-REQ-2.1-02-01
    - **Given:** The visitor is viewing the Men category.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Activate CLOTHES in Breadcrumb.
    - **Then:** The parent CLOTHES category opens with its heading and a keyboard-accessible Men entry.
    - **References:** `\ref[image](IMG-CATEGORY)`
- SCN-REQ-2.1-03 — Browse Women from parent
  - **Step:** STEP-REQ-2.1-03-01
    - **Given:** The visitor has returned from Men to the parent CLOTHES category using Breadcrumb.
    - **When:** Focus Women (link) using the keyboard and activate it.
    - **Then:** Women opens with its heading and Sort by control.
    - **References:** `\ref[image](IMG-CATEGORY)`

### REQ-2.2 Inspect and open product cards

"Product Hummingbird detail t-shirt"(role=region) contains the product image, name, sale and regular prices, and Sale label. Hover reveals "Quick view"(role=button), "Wishlist"(role=link), and "White"(role=button) as the color preview. The keyboard-accessible "Hummingbird detail t-shirt"(role=link) opens that same product's detail with Add to cart.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.2-01 — Inspect card and hover actions
  - **Step:** STEP-REQ-2.2-01-01
    - **Given:** The visitor is viewing Men with Hummingbird detail t-shirt in Product list.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Inspect Product Hummingbird detail t-shirt and hover that region.
    - **Then:** The card shows its image, name, sale price 24, regular price 30 and Sale label; hover reveals Quick view, Wishlist and White color-preview controls.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-2.2-02 — Open card using keyboard
  - **Step:** STEP-REQ-2.2-02-01
    - **Given:** Men Product list includes Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Use keyboard focus to reach its product link and activate it.
    - **Then:** The exact product detail opens with its named heading and Add to cart.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-2.3 Filter catalog results

Selecting "In stock"(role=checkbox) retains the White t-shirt and excludes the out-of-stock Black mug. Selecting "White"(role=checkbox) as the color filter also retains that t-shirt and excludes the Black mug. Entering a number in "Minimum price"(role=spinbutton) retains only products at or above that amount and updates "Product count"(role=status); entering 20 includes the White t-shirt and excludes the Black mug. "Clear all"(role=button) removes applied filters and restores the original results and count.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.3-01 — Filter in-stock products
  - **Step:** STEP-REQ-2.3-01-01
    - **Given:** The unfiltered Men catalog includes in-stock White t-shirt and out-of-stock Black mug.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12, "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Check In stock (checkbox) in Filters.
    - **Then:** White t-shirt remains in Product list and Black mug is excluded.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`
- SCN-REQ-2.3-02 — Filter White color
  - **Step:** STEP-REQ-2.3-02-01
    - **Given:** The unfiltered Men catalog includes White t-shirt and Black mug.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12, "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Check White (checkbox) in Filters.
    - **Then:** White t-shirt remains in Product list and Black mug is excluded.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`
- SCN-REQ-2.3-03 — Filter minimum price
  - **Step:** STEP-REQ-2.3-03-01
    - **Given:** The unfiltered Men catalog includes White t-shirt priced 22 and Black mug priced 12.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Fill Minimum price (spinbutton) with 20 and commit the input.
    - **Then:** White t-shirt remains, Black mug is excluded, and Product count reports the filtered result set.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`
- SCN-REQ-2.3-04 — Clear applied filters
  - **Step:** STEP-REQ-2.3-04-01
    - **Given:** The visitor has opened Men and recorded the original Product count, then applied In stock.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Click Clear all (button).
    - **Then:** In stock is unchecked and the original Product count and previously excluded Black mug return.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.4 Sort products by ascending price

Selecting Price, low to high in "Sort by"(role=combobox) orders the current prices in "Product list"(role=region) ascending while retaining the White t-shirt. Equal-price products have no prescribed tie order.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-SORT · category**

![IMG-SORT · category](reference/sort.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.4-01 — Sort current prices ascending
  - **Step:** STEP-REQ-2.4-01-01
    - **Given:** The unfiltered Men Product list includes White t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Select Price, low to high in Sort by (combobox).
    - **Then:** The displayed current prices are nondecreasing, White t-shirt remains, and the selected sort label is shown; equal-price products have no required tie order.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-SORT)`

### REQ-2.5 Browse additional result pages

The unfiltered Men listing initially shows 12 of 13 products. "Product count"(role=status) displays Showing <start>-<end> of <total> item(s). Clicking "Next"(role=button) within "Pagination"(role=navigation) opens the remaining product slice and updates the range to 13-13 of 13 without changing the total.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.5-01 — Inspect first page and browse second
  - **Step:** STEP-REQ-2.5-01-01
    - **Given:** The unfiltered Men catalog contains 13 products.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Record the first-page product identities, then click Next in Pagination (navigation).
    - **Then:** Initially 12 products and Showing 1-12 of 13 are displayed; the second page shows one different product and Showing 13-13 of 13, preserving total 13.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.6 Filter products on sale

Selecting "On sale"(role=checkbox) within "Filters"(role=region) includes discounted products and excludes undiscounted products according to published catalog. The visible results and "Product count"(role=status) update to the filtered set.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.6-01 — Filter products on sale
  - **Step:** STEP-REQ-2.6-01-01
    - **Given:** The unfiltered Men catalog contains Hummingbird detail t-shirt and White t-shirt with their published catalog attributes; its original Product count is recorded.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Check On sale (checkbox) in Filters.
    - **Then:** Hummingbird detail t-shirt remains in Product list, White t-shirt is excluded, and Product count changes to the filtered result set.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.7 Filter product size

Choosing "M"(role=checkbox) within "Filters"(role=region) includes products offering size M and excludes One size products, using published catalog attributes. The displayed results and "Product count"(role=status) update accordingly.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.7-01 — Filter product size
  - **Step:** STEP-REQ-2.7-01-01
    - **Given:** The unfiltered Men catalog contains White t-shirt and Black mug with their published catalog attributes; its original Product count is recorded.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12, "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Check M (checkbox) in Filters.
    - **Then:** White t-shirt remains in Product list, Black mug is excluded, and Product count changes to the filtered result set.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.8 Filter product composition

Choosing "Cotton"(role=checkbox) within "Filters"(role=region) includes cotton products and excludes ceramic and polyester products according to published catalog. The result set and "Product count"(role=status) update together.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.8-01 — Filter product composition
  - **Step:** STEP-REQ-2.8-01-01
    - **Given:** The unfiltered Men catalog contains White t-shirt and Black mug with their published catalog attributes; its original Product count is recorded.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Check Cotton (checkbox) in Filters.
    - **Then:** White t-shirt remains in Product list, Black mug is excluded, and Product count changes to the filtered result set.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.9 Filter product brand

Choosing "Hummingbird"(role=checkbox) within "Filters"(role=region) retains that brand and excludes Benchmark Basics using published catalog. The displayed results and "Product count"(role=status) reflect the selected brand.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.9-01 — Filter product brand
  - **Step:** STEP-REQ-2.9-01-01
    - **Given:** The unfiltered Men catalog contains Hummingbird detail t-shirt and White t-shirt with their published catalog attributes; its original Product count is recorded.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Check Hummingbird (checkbox) in Filters.
    - **Then:** Hummingbird detail t-shirt remains in Product list, White t-shirt is excluded, and Product count changes to the filtered result set.
    - **References:** `\ref[requirement](REQ-2.1)`, `\ref[image](IMG-CATEGORY)`

### REQ-2.10 Combine filters and clear them

Filters combine by intersection. Selecting "In stock"(role=checkbox) and entering 25 in "Minimum price"(role=spinbutton) retains the cart t-shirt while excluding the White t-shirt priced 22 and the out-of-stock Black mug priced 12. "Clear all"(role=button) restores original first-page product identities and count, clears In stock, and resets Minimum price to empty or 0.

Product list contains one "Product <name>" region per product. Sale price contains only the current monetary amount; discounted cards also expose Regular price. Monetary amounts use USD and a decimal point, with one numeric amount per amount region and an optional currency marker.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-2.10-01 — Combine filters and clear them
  - **Step:** STEP-REQ-2.10-01-01
    - **Given:** The visitor has recorded the unfiltered Men first-page product identities and count; White t-shirt costs 22, Black mug costs 12 and is out of stock, and Hummingbird cart t-shirt costs 25.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 1", "category": "Men", "price": 11, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 2", "category": "Men", "price": 12, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 3", "category": "Men", "price": 13, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}, {"name": "Catalog item 4", "category": "Men", "price": 14, "regular_price": null, "stock": 50, "color": "Black", "size": "One size", "purchasable": true, "composition": "Ceramic", "brand": "Benchmark Basics"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Check In stock, enter 25 in Minimum price and commit it; inspect the results, then click Clear all.
    - **Then:** The intersection includes Hummingbird cart t-shirt and excludes White t-shirt and Black mug; Clear all restores the original identities and count, unchecks In stock, and resets Minimum price to empty or 0.
    - **References:** `\ref[requirement](REQ-2.3)`, `\ref[image](IMG-CATEGORY)`

## REQ-3 Product selection

Product details expose images and thumbnails/zoom, pricing and tax, variants, quantity, description/details tabs, reviews, recently viewed and related products. Variant-dependent pricing and availability update coherently; the source specifies M/White without requiring an invented different price.

Product information contains Sale price, Regular price and product text. Reviews show Average rating: <value>. Stock status shows Available stock: <number>. Selected product and variant state remain consistent across navigation within a flow.

**Type:** FOLDER
**Dependencies:** None

### REQ-3.1 Inspect product details

Opening Hummingbird detail t-shirt displays its heading and "Add to cart"(role=button). "Product images"(role=region) contains exactly one main image named Hummingbird detail t-shirt, thumbnail choices, and "Zoom"(role=button). "Product information"(role=region) shows its name, sale and regular prices, 20% discount, tax information, and regular-fit description.

Product information exposes named Sale price and Regular price amounts. Stock status displays "Available stock: <number>". Selected product and variant remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

For Hummingbird detail t-shirt, the tax-inclusive sale price is USD 24, tax-exclusive price is USD 20, regular price is USD 30 and discount is 20%. The reference is HB-DETAIL, the description and features are regular-fit, the data sheet is cotton, the average rating is 4 with the existing Good fit review, and related products are from Men.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.1-01 — Inspect selected product
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** The seeded Hummingbird detail t-shirt is available in Men.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "tax_rate": 0.2, "detail_images": [{"identity": "Front", "description": "Front view of Hummingbird detail t-shirt"}, {"identity": "Back", "description": "Back view of Hummingbird detail t-shirt"}]}
    - **When:** Open its named product link and inspect Product images and Product information.
    - **Then:** The detail heading and Add to cart identify the product; exactly one main image has its product name, thumbnails and Zoom are available, and information shows sale price 24, regular price 30, 20% discount, tax and regular-fit description.
    - **References:** `\ref[requirement](REQ-2.2)`, `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.2 Select product combination and quantity

Users choose M in "Size"(role=combobox) and "White"(role=radio), with price and stock reflecting that combination. "Quantity"(role=spinbutton) starts at 1; "Increase quantity"(role=button) changes it to 2, while "Decrease quantity"(role=button) returns it to 1 and cannot reduce it below 1. Direct entry of 3 is accepted. Entering 999 exceeds stock, so "Add to cart"(role=button) shows an insufficient-stock alert and adds no product.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.2-01 — Choose M and White
  - **Step:** STEP-REQ-3.2-01-01
    - **Given:** Hummingbird detail t-shirt detail is open with its available variants.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Select M in Size (combobox) and White (radio).
    - **Then:** Size visibly selects M and White is checked for the selected combination.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-3.2-02 — Adjust and directly enter quantity
  - **Step:** STEP-REQ-3.2-02-01
    - **Given:** Hummingbird detail t-shirt detail is open and Quantity starts at 1.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Click Increase quantity, Decrease quantity, and Decrease quantity again; then fill Quantity with 3.
    - **Then:** Quantity changes to 2, returns to 1, remains 1 at the lower bound, then displays the directly entered value 3.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-3.2-03 — Reject quantity exceeding stock
  - **Step:** STEP-REQ-3.2-03-01
    - **Given:** The anonymous visitor is viewing Hummingbird detail t-shirt with an empty cart and stock less than 999.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Fill Quantity with 999 and click Add to cart.
    - **Then:** An insufficient-stock alert appears and Cart remains 0; no success dialog is shown.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.3 Add product to cart and choose next destination

Clicking "Add to cart"(role=button) for one default available Hummingbird cart t-shirt opens "Product successfully added to your shopping cart"(role=dialog) with that product and increases cart count. "Continue shopping"(role=link) closes the dialog and returns to the same detail; "Proceed to checkout"(role=link) opens Shopping cart with that product and its correct subtotal.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-ADD-TO-CART · product**

![IMG-ADD-TO-CART · product](reference/add_to_cart.png)

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.3-01 — Add default product
  - **Step:** STEP-REQ-3.3-01-01
    - **Given:** Hummingbird cart t-shirt detail is open with default M/White variant, Quantity 1 and an empty cart.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Click Add to cart (button).
    - **Then:** Product successfully added to your shopping cart (dialog) identifies Hummingbird cart t-shirt and Cart reports one unit.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-ADD-TO-CART)`, `\ref[image](IMG-CART)`
- SCN-REQ-3.3-02 — Continue on same product
  - **Step:** STEP-REQ-3.3-02-01
    - **Given:** One default Hummingbird cart t-shirt has been added through Add to cart and its success dialog is open.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Activate Continue shopping in the success dialog.
    - **Then:** The dialog closes and the same product detail remains visible.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-ADD-TO-CART)`, `\ref[image](IMG-CART)`
- SCN-REQ-3.3-03 — Proceed from confirmation to cart
  - **Step:** STEP-REQ-3.3-03-01
    - **Given:** One default Hummingbird cart t-shirt has been added through Add to cart and its success dialog is open.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
    - **When:** Activate Proceed to checkout in the success dialog.
    - **Then:** Shopping cart opens with the named product row and subtotal 25.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-ADD-TO-CART)`, `\ref[image](IMG-CART)`

### REQ-3.4 Read description and product details

Selecting "Description"(role=tab) displays its corresponding named tabpanel with the regular-fit description. Selecting "Product Details"(role=tab) displays the matching tabpanel with Reference HB-DETAIL, a cotton Data sheet, and regular-fit Features.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.4-01 — Read description tab
  - **Step:** STEP-REQ-3.4-01-01
    - **Given:** Hummingbird detail t-shirt detail is open.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Select Description (tab).
    - **Then:** Description is selected and its named tabpanel displays the regular-fit product description.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-3.4-02 — Read details tab
  - **Step:** STEP-REQ-3.4-02-01
    - **Given:** Hummingbird detail t-shirt detail is open.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Select Product Details (tab).
    - **Then:** Product Details is selected and its tabpanel shows Reference HB-DETAIL, a cotton Data sheet and regular-fit Features.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.5 Inspect reviews and enforce visitor sign-in prompts

"Reviews"(role=region) shows the seeded Good fit review and average rating 4. For an anonymous visitor, "Write your review"(role=button) opens "Sign in required"(role=dialog), identifying Hummingbird detail t-shirt, without submitting a review. "Wishlist"(role=link) produces the same product-specific sign-in prompt without storing wishlist membership.

Reviews displays "Average rating: <value>".

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.5-01 — Read existing review
  - **Step:** STEP-REQ-3.5-01-01
    - **Given:** Hummingbird detail t-shirt has a seeded Good fit review and average rating 4.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "review": {"text": "Good fit", "average_rating": 4}}
    - **When:** Open the product detail and inspect Reviews.
    - **Then:** Reviews displays Good fit and average rating 4.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-3.5-02 — Require sign-in before review
  - **Step:** STEP-REQ-3.5-02-01
    - **Given:** An anonymous visitor is viewing Hummingbird detail t-shirt and its existing Reviews.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "review": {"text": "Good fit", "average_rating": 4}}
    - **When:** Click Write your review (button).
    - **Then:** Sign in required (dialog) identifies the product, and existing Reviews remains unchanged without a newly submitted review.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`
- SCN-REQ-3.5-03 — Require sign-in before wishlist
  - **Step:** STEP-REQ-3.5-03-01
    - **Given:** An anonymous visitor is viewing Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Activate Wishlist (link).
    - **Then:** Sign in required (dialog) identifies the product and the visitor remains anonymous; the wishlist action does not report successful membership.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.6 Discover recently viewed and related products

After visiting Hummingbird detail t-shirt, "Recently viewed"(role=region) includes that product. "Related products"(role=region) contains a different Men product with a keyboard-accessible opening entry.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.6-01 — Inspect recommendations and viewing history
  - **Step:** STEP-REQ-3.6-01-01
    - **Given:** The visitor has opened Hummingbird detail t-shirt from Men.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "White t-shirt", "category": "Men", "price": 22, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Benchmark Basics"}, {"name": "Black mug", "category": "Men", "price": 12, "regular_price": null, "stock": 0, "color": "Black", "size": "One size", "purchasable": false, "composition": "Ceramic", "brand": "Benchmark Basics"}]}
    - **When:** Inspect Related products and Recently viewed.
    - **Then:** Recently viewed contains Hummingbird detail t-shirt; Related products contains a different seeded Men product with a keyboard-accessible opening entry.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.7 Switch product thumbnail image

"Product images"(role=region) offers keyboard-accessible "Front"(role=button) and "Back"(role=button) thumbnails. Back replaces the single main image with the distinct back view while retaining the product's accessible name; Front restores the original front image. Switching images does not change the selected product.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.7-01 — Switch product thumbnail image
  - **Step:** STEP-REQ-3.7-01-01
    - **Given:** Hummingbird detail t-shirt detail shows its Front main image; its original image source is recorded.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_images": [{"identity": "Front", "description": "Front view of Hummingbird detail t-shirt"}, {"identity": "Back", "description": "Back view of Hummingbird detail t-shirt"}]}
    - **When:** Click Back in Product images, inspect the main image, then click Front.
    - **Then:** Back displays a different image source with the same product accessible name; Front restores the original source, and the selected product heading is unchanged.
    - **References:** `\ref[requirement](REQ-3.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.8 Open and close enlarged product image

Clicking "Zoom"(role=button) in Product images opens "Product image"(role=dialog) with the currently selected product image and a visible Front view or Back view caption. "Close"(role=button) dismisses the enlargement without changing the product or selected image.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.8-01 — Open and close enlarged product image
  - **Step:** STEP-REQ-3.8-01-01
    - **Given:** Hummingbird detail t-shirt detail is open and Back has been selected in Product images.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_images": [{"identity": "Front", "description": "Front view of Hummingbird detail t-shirt"}, {"identity": "Back", "description": "Back view of Hummingbird detail t-shirt"}]}
    - **When:** Click Zoom, inspect Product image (dialog), then click its Close button.
    - **Then:** The dialog displays one enlarged product image and Back view caption; closing it preserves the product heading and selected back image.
    - **References:** `\ref[requirement](REQ-3.7)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.9 Update price and stock for selected variant

Choosing L in "Size"(role=combobox) and "Black"(role=radio) updates "Product information"(role=region) to the published catalog variant's sale price 36, regular price 45, and "Stock"(role=status) displaying Available stock: 2. Selecting M and "White"(role=radio) restores sale price 24, regular price 30, and Available stock: 50. Both monetary values and stock must follow the actual selected combination rather than only changing the selection controls.

Product information exposes named Sale price and Regular price amounts. Stock status displays "Available stock: <number>". Selected product and variant remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-3.9-01 — Update price and stock for selected variant
  - **Step:** STEP-REQ-3.9-01-01
    - **Given:** Hummingbird detail t-shirt detail is open with the catalog variant data.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Select L in Size and Black (radio), inspect information, then select M and White (radio).
    - **Then:** L/Black shows sale price 36, regular price 45 and Available stock: 2; M/White restores price 24, regular price 30 and Available stock: 50.
    - **References:** `\ref[requirement](REQ-3.2)`, `\ref[image](IMG-PRODUCT-DETAIL)`

## REQ-4 Cart management

Cart rows identify the product and selected combination, image, unit price, quantity and subtotal. Cart summary reconciles monetary totals. Visitors can continue browsing or start checkout.

Cart rows expose Unit price and Subtotal; Cart summary exposes Items subtotal, Shipping, Total and Discount when applicable. Variant text identifies Size: <size> and Color: <color>. Cart count counts units. Cart state remains consistent across navigation within a flow.

**Type:** FOLDER
**Dependencies:** None

### REQ-4.1 Inspect cart contents and summary

After UI addition, Shopping cart contains exactly one "Hummingbird cart t-shirt"(role=row) with image, M/White combination, Unit price 25, "Quantity"(role=spinbutton) set to 1, Subtotal 25, and "Delete"(role=button). "Cart summary"(role=region) reconciles Items subtotal 25, Shipping 5, and Total 30 including tax. Discount appears only when applicable and is absent for this undiscounted product.

Cart rows expose named Unit price and Subtotal amounts. Cart summary exposes Items subtotal, Shipping, Total, and Discount when applicable. Variant text identifies "Size: <size>" and "Color: <color>". Cart count counts units, and cart state remains consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Each cart row identifies its product and selected variant. Cart count counts units, while Unit price, Subtotal, Items subtotal, Shipping, Total and any Discount reconcile consistently across navigation.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.1-01 — Inspect cart row and totals
  - **Step:** STEP-REQ-4.1-01-01
    - **Given:** The visitor has added one default M/White Hummingbird cart t-shirt through UI and opened Shopping cart from the success dialog.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
    - **When:** Inspect its named row and Cart summary.
    - **Then:** Exactly one row shows image, M/White, Unit price 25, Quantity 1, Subtotal 25 and Delete; summary shows Items subtotal 25, Shipping 5 and Total 30 including tax, with no Discount.
    - **References:** `\ref[requirement](REQ-3.3)`, `\ref[image](IMG-CART)`

### REQ-4.2 Change or remove cart items

Clicking "Increase quantity"(role=button) within "Hummingbird cart t-shirt"(role=row) changes quantity from 1 to 2, row Subtotal to 50, and Total in "Cart summary"(role=region) to 55. "Delete"(role=button) on that row removes it, displays the empty-cart message, and recalculates Items subtotal and Total to 0.

Cart rows expose named Unit price and Subtotal amounts. Cart summary exposes Items subtotal, Shipping, Total, and Discount when applicable. Variant text identifies "Size: <size>" and "Color: <color>". Cart count counts units, and cart state remains consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Each cart row identifies its product and selected variant. Cart count counts units, while Unit price, Subtotal, Items subtotal, Shipping, Total and any Discount reconcile consistently across navigation.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.2-01 — Increase cart quantity
  - **Step:** STEP-REQ-4.2-01-01
    - **Given:** Shopping cart contains one M/White Hummingbird cart t-shirt priced 25 and quantity 1, added through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
    - **When:** Click Increase quantity within that product row.
    - **Then:** Quantity becomes 2, row Subtotal becomes 50 and Cart summary Total becomes 55.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-CART)`
- SCN-REQ-4.2-02 — Delete cart product
  - **Step:** STEP-REQ-4.2-02-01
    - **Given:** Shopping cart contains one Hummingbird cart t-shirt added through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
    - **When:** Click Delete within its named row.
    - **Then:** The product row disappears, an empty-cart message appears, and Items subtotal and Total both become 0.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-CART)`

### REQ-4.3 Continue browsing or begin checkout

From Shopping cart, "Continue shopping"(role=link) opens Men with the cart t-shirt available. "Proceed to checkout"(role=link) opens "Personal Information"(role=region) and "Order summary"(role=region) containing the selected product. Both transitions retain the cart.

Cart rows expose named Unit price and Subtotal amounts. Cart summary exposes Items subtotal, Shipping, Total, and Discount when applicable. Variant text identifies "Size: <size>" and "Color: <color>". Cart count counts units, and cart state remains consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Each cart row identifies its product and selected variant. Cart count counts units, while Unit price, Subtotal, Items subtotal, Shipping, Total and any Discount reconcile consistently across navigation.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.3-01 — Return to browsing
  - **Step:** STEP-REQ-4.3-01-01
    - **Given:** Shopping cart contains one Hummingbird cart t-shirt added through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Activate Continue shopping (link).
    - **Then:** Men opens with Hummingbird cart t-shirt available and the header Cart still reports one unit.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-CART)`, `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-CHECKOUT)`
- SCN-REQ-4.3-02 — Enter checkout with selected cart
  - **Step:** STEP-REQ-4.3-02-01
    - **Given:** Shopping cart contains one Hummingbird cart t-shirt added through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Activate Proceed to checkout (link).
    - **Then:** Personal Information and Order summary open; the summary still contains the selected Hummingbird cart t-shirt.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-CART)`, `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-CHECKOUT)`

### REQ-4.4 Edit cart quantity directly

Entering 3 in "Quantity"(role=spinbutton) within "Hummingbird cart t-shirt"(role=row) and committing on blur updates its Subtotal to 75 and "Cart summary"(role=region) to Items subtotal 75 and Total 80. The header "Cart"(role=link) reports a count of three units.

Cart rows expose named Unit price and Subtotal amounts. Cart summary exposes Items subtotal, Shipping, Total, and Discount when applicable. Variant text identifies "Size: <size>" and "Color: <color>". Cart count counts units, and cart state remains consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Each cart row identifies its product and selected variant. Cart count counts units, while Unit price, Subtotal, Items subtotal, Shipping, Total and any Discount reconcile consistently across navigation.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.4-01 — Edit cart quantity directly
  - **Step:** STEP-REQ-4.4-01-01
    - **Given:** Shopping cart contains one Hummingbird cart t-shirt priced 25, quantity 1 and shipping 5.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
    - **When:** Fill Quantity within its row with 3, then blur that field.
    - **Then:** Row Subtotal and summary Items subtotal become 75, Total becomes 80, and header Cart reports three units.
    - **References:** `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-CART)`

### REQ-4.5 Carry selected variant into cart

Users choose L in "Size"(role=combobox), select "Black"(role=radio), enter 2 in "Quantity"(role=spinbutton), and click "Add to cart"(role=button). Shopping cart displays "Hummingbird detail t-shirt"(role=row) with that exact variant, quantity, and sale unit price 36. "Cart summary"(role=region) shows Items subtotal 72, Shipping 5, Total 77, and informational Discount 18, calculated as 2×(45−36). The already-discounted subtotal is not discounted a second time.

Cart rows expose named Unit price and Subtotal amounts. Cart summary exposes Items subtotal, Shipping, Total, and Discount when applicable. Variant text identifies "Size: <size>" and "Color: <color>". Cart count counts units, and cart state remains consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Each cart row identifies its product and selected variant. Cart count counts units, while Unit price, Subtotal, Items subtotal, Shipping, Total and any Discount reconcile consistently across navigation.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-4.5-01 — Carry selected variant into cart
  - **Step:** STEP-REQ-4.5-01-01
    - **Given:** Hummingbird detail t-shirt detail is open with an empty cart; L/Black has stock 2 and sale/regular prices 36/45.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "tax_rate": 0.2, "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Select L and Black, enter Quantity 2, click Add to cart and use Proceed to checkout in the success dialog.
    - **Then:** The cart row retains L/Black and quantity 2 at unit price 36; Items subtotal is 72, Shipping 5, informational Discount 18 and Total 77, without deducting the discount again.
    - **References:** `\ref[requirement](REQ-3.9)`, `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`, `\ref[image](IMG-CART)`

## REQ-5 Checkout completion

Checkout progresses Personal Information → Addresses → Shipping Method → Payment → Order Confirmation; completed steps collapse and can be edited. Anonymous users can access login, registration or guest information; concrete guest completion is unspecified. Summary and prices stay coherent. Shipping addresses may be created or edited and invoice address separated.

Order summary and checkout steps Personal Information, Addresses, Shipping Method and Payment are named regions; Continue actions are scoped to their step. Expanded steps expose their inputs; collapsed completed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Order details identify Quantity: <value>. Step data remain consistent across navigation within a flow.

For available fulfillment choices: Carrier, country and payment publication are outside scope. Terms agreement is available through a separate link.

**Type:** FOLDER
**Dependencies:** None

### REQ-5.1 Start checkout and inspect customer information

Anonymous checkout with the checkout-step t-shirt opens "Personal Information"(role=region) and "Order summary"(role=region). For signed-in checkout_user, Personal Information displays prestashop_checkout_user@example.com; its "Continue"(role=button) opens "Addresses"(role=region) if that step is not already active.

Anonymous checkout exposes login, registration, or guest-information entry. Concrete guest completion is unspecified.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.1-01 — Start anonymous checkout
  - **Step:** STEP-REQ-5.1-01-01
    - **Given:** An anonymous visitor has added one Hummingbird checkout-step t-shirt and opened Shopping cart through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
    - **When:** Activate Proceed to checkout.
    - **Then:** Personal Information opens for the anonymous customer, and Order summary contains Hummingbird checkout-step t-shirt.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[image](IMG-CART)`, `\ref[image](IMG-CHECKOUT)`
- SCN-REQ-5.1-02 — Inspect signed-in customer
  - **Step:** STEP-REQ-5.1-02-01
    - **Given:** Verified checkout_user has signed in through Email and Password, created Home through the address UI, and added one Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Proceed from Shopping cart into checkout; inspect Personal Information and click its Continue if Addresses is not already active.
    - **Then:** Personal Information identifies prestashop_checkout_user@example.com and Addresses offers Home without losing the order product.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[requirement](REQ-7.3)`, `\ref[image](IMG-CART)`, `\ref[image](IMG-CHECKOUT)`

### REQ-5.2 Select shipping address

After checkout_address_user creates Home through UI, "Addresses"(role=region) offers "Home"(role=radio) with 1 Commerce Road. Selecting it visibly marks that address; "Continue"(role=button) progresses to Shipping Method while retaining the same order product.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-ADDRESS · checkout**

![IMG-CHECKOUT-ADDRESS · checkout](reference/checkout_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.2-01 — Select Home address
  - **Step:** STEP-REQ-5.2-01-01
    - **Given:** Signed-in checkout_address_user has created Home at 1 Commerce Road through UI and entered Addresses with one Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_address_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_cost": 5}
    - **When:** Select Home (radio), inspect its checked state and street, then click Continue within Addresses.
    - **Then:** Home is visibly selected with 1 Commerce Road; Shipping Method opens and Order summary retains the selected product.
    - **References:** `\ref[requirement](REQ-5.1)`, `\ref[requirement](REQ-7.3)`, `\ref[image](IMG-CHECKOUT-ADDRESS)`

### REQ-5.3 Create checkout shipping address

In checkout Addresses, checkout_new_address_user clicks "Add new address"(role=button) and completes "Alias"(role=textbox), "First name"(role=textbox), "Last name"(role=textbox), "Address"(role=textbox), "Postal code"(role=textbox), "City"(role=textbox), "Country"(role=combobox), and "Phone"(role=textbox). "Save"(role=button) saves Office for Store User at 1 Commerce Road, 200000 Shanghai, China, 13800000020. The saved Office address appears in checkout as "Office"(role=radio).

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-ADDRESS · checkout**

![IMG-CHECKOUT-ADDRESS · checkout](reference/checkout_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.3-01 — Save new checkout address
  - **Step:** STEP-REQ-5.3-01-01
    - **Given:** Signed-in checkout_new_address_user has no saved address and is at checkout Addresses with Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_new_address_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Click Add new address; enter Alias Office, First name Store, Last name User, Address 1 Commerce Road, Postal code 200000, City Shanghai, Country China and Phone 13800000020, then click Save.
    - **Then:** The saved Office address is visible in Addresses with its entered street and available for checkout selection; the order product is retained.
    - **References:** `\ref[requirement](REQ-5.1)`, `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-CHECKOUT-ADDRESS)`

### REQ-5.4 Separate invoice address and choose carrier

With checkout_invoice_user's UI-created Home available, clearing "Use same address"(role=checkbox) reveals "Invoice address"(role=region), including Home. Continuing with Home opens "Shipping Method"(role=region), where "Delivery"(role=radio) displays cost 5 and visibly reflects selection. "Order summary"(role=region) includes the checkout-step t-shirt price 26 plus shipping 5, totaling 31.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-SHIPPING · checkout**

![IMG-CHECKOUT-SHIPPING · checkout](reference/checkout_shipping.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.4-01 — Use separate invoice address
  - **Step:** STEP-REQ-5.4-01-01
    - **Given:** Signed-in checkout_invoice_user has created Home through UI and is at Addresses with Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Uncheck Use same address (checkbox).
    - **Then:** Invoice address appears and includes Home as an available billing address.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT-SHIPPING)`
- SCN-REQ-5.4-02 — Choose Delivery
  - **Step:** STEP-REQ-5.4-02-01
    - **Given:** Signed-in checkout_invoice_user has created Home through UI and reached Addresses with Hummingbird checkout-step t-shirt priced 26.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5}
    - **When:** Select Home, click Continue in Addresses, then select Delivery (radio) in Shipping Method.
    - **Then:** Delivery is checked with cost 5; Order summary retains the product and shows total 31.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT-SHIPPING)`

### REQ-5.5 Choose payment and read terms

Continuing after Delivery selection opens "Payment"(role=region), where users select "Bank wire"(role=radio) and agree through "Terms and conditions"(role=checkbox). The separate "Terms and conditions"(role=link) opens "Terms and conditions"(role=region) with agreement content. "Place order"(role=button) completes the order only after agreement.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-PAYMENT · checkout**

![IMG-CHECKOUT-PAYMENT · checkout](reference/checkout_payment.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.5-01 — Choose bank wire and read terms
  - **Step:** STEP-REQ-5.5-01-01
    - **Given:** A signed-in checkout customer has created Home, added Hummingbird checkout-step t-shirt, completed Home and Delivery, and reached Payment.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
    - **When:** Select Bank wire (radio), check Terms and conditions (checkbox), then activate the separate Terms and conditions link.
    - **Then:** Bank wire and agreement are selected; the Terms and conditions region displays agreement content.
    - **References:** `\ref[requirement](REQ-5.4)`, `\ref[image](IMG-CHECKOUT-PAYMENT)`
- SCN-REQ-5.5-02 — Require terms before completion
  - **Step:** STEP-REQ-5.5-02-01
    - **Given:** The signed-in customer has reached Payment with Home and Delivery completed and Hummingbird checkout-step t-shirt retained.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
    - **When:** Select Bank wire, leave Terms and conditions unchecked, and attempt Place order if the action is enabled.
    - **Then:** Order confirmation is not displayed; the product remains in Order summary and agreement is still required, whether Place order is disabled or the attempt is rejected.
    - **References:** `\ref[requirement](REQ-5.4)`, `\ref[image](IMG-CHECKOUT-PAYMENT)`

### REQ-5.6 Place order and inspect completion

Using checkout_6_6_user with the order-confirmation t-shirt or checkout_6_7_user with the order-complete t-shirt, users complete Home, Delivery, Bank wire, and agreement, then click "Place order"(role=button). Order confirmation displays the chosen product; "Order reference"(role=region) contains a nonempty assigned reference, and "Order details"(role=region) shows product, quantity, amounts, shipping, and payment. "Continue shopping"(role=link) returns home with Search, My account, and Cart.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

Order details identifies "Quantity: <value>".

For new order: Created through REQ-5.6; assigned reference is observed, never predetermined.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**IMG-CHECKOUT-SUMMARY · order_confirmation**

![IMG-CHECKOUT-SUMMARY · order_confirmation](reference/checkout_summary.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.6-01 — Place order for selected product
  - **Step:** STEP-REQ-5.6-01-01
    - **Given:** Signed-in checkout_6_6_user has created Home and added one Hummingbird order-confirmation t-shirt through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_6_6_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
    - **When:** Proceed to checkout, select Home and continue, select Delivery and continue, select Bank wire, check Terms and conditions, then click Place order.
    - **Then:** Order confirmation opens and identifies Hummingbird order-confirmation t-shirt.
    - **References:** `\ref[requirement](REQ-5.5)`, `\ref[image](IMG-CHECKOUT)`, `\ref[image](IMG-CHECKOUT-SUMMARY)`
- SCN-REQ-5.6-02 — Inspect completed order and continue shopping
  - **Step:** STEP-REQ-5.6-02-01
    - **Given:** Signed-in checkout_6_7_user has created Home and added one Hummingbird order-complete t-shirt through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_6_7_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
    - **When:** Complete checkout with Home, Delivery, Bank wire and checked Terms and conditions; click Place order, inspect confirmation, then activate Continue shopping.
    - **Then:** Confirmation has a nonempty Order reference; Order details shows the product, quantity 1, total 33, Home, Delivery and Bank wire. Continue shopping returns home with Search, My account and Cart available.
    - **References:** `\ref[requirement](REQ-5.5)`, `\ref[image](IMG-CHECKOUT)`, `\ref[image](IMG-CHECKOUT-SUMMARY)`

### REQ-5.7 Edit shipping address during checkout

Within "Addresses"(role=region), "Edit address Home"(role=button) opens the existing Home address form. Changing its street to 88 Market Street and clicking "Save"(role=button) updates the saved address, which remains selectable through "Home"(role=radio), without altering the cart product or summary. Continue then opens Shipping Method with the updated address available.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-ADDRESS · checkout**

![IMG-CHECKOUT-ADDRESS · checkout](reference/checkout_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.7-01 — Edit shipping address during checkout
  - **Step:** STEP-REQ-5.7-01-01
    - **Given:** A signed-in checkout customer has created Home at 1 Commerce Road and reached Addresses with Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_address_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_cost": 5}
    - **When:** Click Edit address Home, replace Address with 88 Market Street, click Save, select Home and click Continue in Addresses.
    - **Then:** Home shows 88 Market Street, Shipping Method opens, and Order summary retains the same selected product.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT-ADDRESS)`

### REQ-5.8 Reopen completed shipping step

At "Payment"(role=region) after completing Home and Delivery, clicking "Edit Shipping Method"(role=button) reopens "Shipping Method"(role=region) with "Delivery"(role=radio) still selected. "Continue"(role=button) returns to Payment while preserving the cart product and total 31. Reopening the step does not place an order.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-SHIPPING · checkout**

![IMG-CHECKOUT-SHIPPING · checkout](reference/checkout_shipping.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.8-01 — Reopen completed shipping step
  - **Step:** STEP-REQ-5.8-01-01
    - **Given:** The signed-in customer has completed Home and Delivery and reached Payment with Hummingbird checkout-step t-shirt and total 31.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire"}
    - **When:** Click Edit Shipping Method, inspect Delivery, then click Continue within Shipping Method.
    - **Then:** Shipping Method reopens with Delivery checked; Payment returns with the same product and total 31, and no Order confirmation is created.
    - **References:** `\ref[requirement](REQ-5.5)`, `\ref[image](IMG-CHECKOUT-SHIPPING)`

### REQ-5.9 Collapse completed address step and reopen it

Completing "Addresses"(role=region) hides its editable controls, retains its summary and "Edit Addresses"(role=button), and activates "Shipping Method"(role=region). Clicking Edit Addresses reopens "Home"(role=radio) selection without losing the chosen address or order product. Available controls, rather than DOM layout, make completion and reopening observable.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-5.9-01 — Collapse completed address step and reopen it
  - **Step:** STEP-REQ-5.9-01-01
    - **Given:** A signed-in customer has UI-created Home and is at Addresses with Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_address_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5}
    - **When:** Select Home and click Continue, inspect the completed step, then click Edit Addresses.
    - **Then:** Home selection controls collapse, Edit Addresses and Delivery are available; reopening shows Home still checked and preserves the order product.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT)`

## REQ-6 Customer access

Visitors sign in, register, request password reset and sign out. Password masking and remember-me controls are visible; remember-me lifetime and actual email delivery are unspecified.

Password reset confirmation is a named status message.

**Type:** FOLDER
**Dependencies:** None

### REQ-6.1 Sign in with password visibility and remember option

Clicking "Sign in"(role=button) opens "Email"(role=textbox), masked "Password"(role=textbox), a Sign in submit action, and "No account? Create one here"(role=link). "SHOW"(role=button) reveals the password and "Remember me"(role=checkbox) is selectable. Valid verified Store User credentials sign in, showing Store User, "My account"(role=link), and "Sign out"(role=button). Registration does not replace the source's verified-account fixture.

Remember-me lifetime is unspecified.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Remember-me lifetime is unspecified; successful authentication does not imply an invented expiry guarantee.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.1-01 — Open sign-in entry
  - **Step:** STEP-REQ-6.1-01-01
    - **Given:** An anonymous visitor is on the homepage.
    - **When:** Activate Sign in in Global navigation.
    - **Then:** Email and masked Password fields, the Sign in submit button and No account? Create one here link are visible.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-MY-ACCOUNT)`
- SCN-REQ-6.1-02 — Reveal password and sign in
  - **Step:** STEP-REQ-6.1-02-01
    - **Given:** The anonymous visitor has opened Sign in and verified Store User credentials are prestashop_user@example.com / ShopPass123!.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Enter those credentials, click SHOW, check Remember me, then click the Sign in submit button.
    - **Then:** Email retains its value, Password becomes visible with the entered value, Remember me is checked, and successful sign-in exposes Store User, My account and Sign out in Global navigation.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-MY-ACCOUNT)`

### REQ-6.2 Register customer

From Sign in, "No account? Create one here"(role=link) opens registration with "Mr."(role=radio), "First name"(role=textbox), "Last name"(role=textbox), "Email"(role=textbox), "Password"(role=textbox), "Birthdate"(role=textbox), and "Receive offers"(role=checkbox), "Newsletter"(role=checkbox), and "Terms"(role=checkbox). Entering New Customer, unused new_customer_7_3@example.com, ShopPass123!, 1995-08-21, and all stated choices, then clicking "Save"(role=button), creates a signed-in account showing New Customer.

For registered customer: Created through REQ-6.2 using new_customer_7_3@example.com.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-REGISTER · register**

![IMG-REGISTER · register](reference/register.png)

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.2-01 — Create new customer
  - **Step:** STEP-REQ-6.2-01-01
    - **Given:** An anonymous visitor has opened Sign in; new_customer_7_3@example.com is unused in this scenario world.
    - **When:** Activate No account? Create one here; select Mr., enter First name New, Last name Customer, Email new_customer_7_3@example.com, Password ShopPass123! and Birthdate 1995-08-21, check Receive offers, Newsletter and Terms, then click Save.
    - **Then:** Registration creates a signed-in customer identified as New Customer.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-REGISTER)`, `\ref[image](IMG-HOMEPAGE)`

### REQ-6.3 Request password reset

Clicking "Forgot your password?"(role=link) from Sign in opens "Email"(role=textbox) and "Send"(role=button). Submitting existing prestashop_user@example.com displays an email-sent confirmation mentioning that address; actual mailbox delivery is not asserted.

Password reset confirmation is a named status message.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Password reset confirmation is a named status message; actual email delivery is unspecified.

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**IMG-FORGOT-PASSWORD · password_recovery**

![IMG-FORGOT-PASSWORD · password_recovery](reference/forgot_password.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.3-01 — Request existing-account reset
  - **Step:** STEP-REQ-6.3-01-01
    - **Given:** An anonymous visitor has opened Sign in and prestashop_user@example.com is an existing verified account.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Activate Forgot your password?, enter that address in Email and click Send.
    - **Then:** Password reset confirmation reports that a reset email was sent and mentions prestashop_user@example.com; mailbox delivery is outside this oracle.
    - **References:** `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-FORGOT-PASSWORD)`

### REQ-6.4 Sign out to storefront

The signed-in Store User clicks "Sign out"(role=button) from My account and returns home, which shows "Sign in"(role=button), Cart, and Hummingbird detail t-shirt. Sign out is no longer available.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-LOGOUT · home**

![IMG-LOGOUT · home](reference/logout.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-6.4-01 — Sign out from account
  - **Step:** STEP-REQ-6.4-01-01
    - **Given:** Store User has signed in through the sign-in UI and opened My account.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Activate Sign out in Global navigation.
    - **Then:** The homepage displays Sign in, Cart and Hummingbird detail t-shirt, and Sign out is unavailable.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-LOGOUT)`

## REQ-7 Account management

Signed-in customers inspect account overview, edit credentials, manage addresses, view history/invoices, reorder and manage wishlists. Mutations affect the corresponding business identity, not a neighboring entry.

Account overview and Order history are named regions. "Profile update"(role=status) identifies the update message.

**Type:** FOLDER
**Dependencies:** None

### REQ-7.1 Inspect account overview

Clicking "My account"(role=link) after signing in displays My account heading, Store User, and "Information"(role=link), "Addresses"(role=link), "Order history and details"(role=link), and "Wishlist"(role=link) entry points.

Account overview is a named region.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.1-01 — Inspect account overview
  - **Step:** STEP-REQ-7.1-01-01
    - **Given:** Verified Store User has signed in through Email and Password.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Activate My account (link).
    - **Then:** My account heading and Store User appear with Information, Addresses, Order history and details and Wishlist entry links.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-MY-ACCOUNT)`

### REQ-7.2 Change customer email and password

The profile_user opens "Information"(role=link) with "Email"(role=textbox), "Current password"(role=textbox), and "New password"(role=textbox). Entering ShopPass123! as the current password, changing Email to prestashop_profile_user_next@example.com, and clicking "Save"(role=button) displays "Profile update"(role=status) confirmation and the new email while retaining the old password. A subsequent save with current password ShopPass123! and new password ShopPass456! confirms the password change. The resulting credentials permit sign-in.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Profile update is the named status identifying the update result. Existing account verification is outside scope; the new profile email is initially unused.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-MY-ACCOUNT-INFO · account_information**

![IMG-MY-ACCOUNT-INFO · account_information](reference/my_account_info.png)

**IMG-LOGIN · login**

![IMG-LOGIN · login](reference/login.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.2-01 — Save email then password
  - **Step:** STEP-REQ-7.2-01-01
    - **Given:** Verified profile_user has signed in using ShopPass123! and opened Information.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_profile_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Enter Current password ShopPass123!, replace Email with prestashop_profile_user_next@example.com and click Save; then enter Current password ShopPass123! and New password ShopPass456! and click Save again; sign out and sign in with the new credentials.
    - **Then:** Each save reports Profile update success; the new email remains displayed after the first save and the new email/password pair successfully signs in after the second.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-INFO)`, `\ref[image](IMG-LOGIN)`

### REQ-7.3 Create and view addresses

Clicking "Addresses"(role=link) displays each saved address as "{alias}"(role=article), containing its values and Update and Delete actions. "Create new address"(role=button) opens "Alias"(role=textbox), "First name"(role=textbox), "Last name"(role=textbox), "Address"(role=textbox), "Postal code"(role=textbox), "City"(role=textbox), "Country"(role=combobox), and "Phone"(role=textbox), displaying entered values before submission. "Save"(role=button) with Office and shared examples address values creates one Office article; Home setup uses the same creation behavior and values.

For customer address: Created through REQ-7.3 or checkout REQ-5.3. Home/Office: Store User, 1 Commerce Road, 200000, Shanghai, China, 13800000020. Home is created in UI setup before selection/edit/delete scenarios. Updated street: 88 Market Street.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

The existing customer address books start empty. Home is created through the address UI before address selection, editing or deletion; it is not an extra preloaded address.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-MY-ACCOUNT-ADDRESS · account_addresses**

![IMG-MY-ACCOUNT-ADDRESS · account_addresses](reference/my_account_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.3-01 — View Home address
  - **Step:** STEP-REQ-7.3-01-01
    - **Given:** Signed-in address_view_user has created Home through the normal address UI using Store User, 1 Commerce Road, 200000 Shanghai, China and 13800000020.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}, {"email": "prestashop_address_view_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Open Addresses from Account overview.
    - **Then:** Home (article) shows those saved values and its Update and Delete actions.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`
- SCN-REQ-7.3-02 — Create Office address
  - **Step:** STEP-REQ-7.3-02-01
    - **Given:** Signed-in address_create_user has opened Addresses and has no address articles.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}, {"email": "prestashop_address_create_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Click Create new address; enter Alias Office, First name Store, Last name User, Address 1 Commerce Road, Postal code 200000, City Shanghai, Country China and Phone 13800000020; inspect entered values, then click Save.
    - **Then:** Exactly one Office article displays the saved address values with Update and Delete controls.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`

### REQ-7.4 Edit or delete named address

The address_edit_user or address_delete_user first creates Home through UI. In "Home"(role=article), "Update"(role=button) opens its current Alias and street values. Editing the street to 88 Market Street and clicking "Save"(role=button) updates that same article. Alternatively, "Delete"(role=button) within Home removes only that address and returns to the address list.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-ADDRESS · account_addresses**

![IMG-MY-ACCOUNT-ADDRESS · account_addresses](reference/my_account_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.4-01 — Update Home street
  - **Step:** STEP-REQ-7.4-01-01
    - **Given:** Signed-in address_edit_user has created Home at 1 Commerce Road through UI and opened Addresses.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_address_edit_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Click Update within Home, verify Alias Home and the existing street, replace Address with 88 Market Street and click Save.
    - **Then:** The same Home article shows 88 Market Street instead of the original street.
    - **References:** `\ref[requirement](REQ-7.3)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`
- SCN-REQ-7.4-02 — Delete Home address
  - **Step:** STEP-REQ-7.4-02-01
    - **Given:** Signed-in address_delete_user has created Home through UI and opened Addresses.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_address_delete_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Click Delete within Home and confirm the deletion prompt.
    - **Then:** Home is removed and the address list is displayed.
    - **References:** `\ref[requirement](REQ-7.3)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`

### REQ-7.5 Read historical orders and details

Clicking "Order history and details"(role=link) shows the historical "PS-HISTORY-001"(role=row), with the order-history t-shirt, reference, date 2026-07-18, Delivered status, and Total 34. "Details"(role=link) opens "Order details"(role=region) for that order, containing its product, shared examples shipping information, and Bank wire payment.

Order history is a named region.

For completed delivered historical order: Exactly one initial historical order. The scoped checkout flow cannot create Delivered status or the historical date/reference; the historical order already has these fixed values.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Displayed dates use UTC and the shared clock 2026-10-06T12:00:00Z; carousel transitions use elapsed time.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-MY-ACCOUNT-ORDER · account_orders**

![IMG-MY-ACCOUNT-ORDER · account_orders](reference/my_account_order.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.5-01 — Inspect historical order list
  - **Step:** STEP-REQ-7.5-01-01
    - **Given:** Verified order_history_user has the seeded historical order PS-HISTORY-001.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_order_history_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - completed delivered historical order: {"owner": "prestashop_order_history_user@example.com", "reference": "PS-HISTORY-001", "date": "2026-07-18", "status": "Delivered", "product": "Hummingbird order-history t-shirt", "quantity": 1, "product_amount": 29, "shipping": 5, "total": 34, "address": "1 Commerce Road, Shanghai 200000, China", "payment": "Bank wire", "invoice": "Downloadable PDF for PS-HISTORY-001"}
    - **When:** Sign in and open Order history and details from My account.
    - **Then:** The PS-HISTORY-001 row shows Hummingbird order-history t-shirt, 2026-07-18, Delivered and total 34, with Details, Reorder and PDF entries.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ORDER)`
- SCN-REQ-7.5-02 — Inspect selected order details
  - **Step:** STEP-REQ-7.5-02-01
    - **Given:** Signed-in order_history_user is viewing Order history and details with seeded PS-HISTORY-001.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_order_history_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - completed delivered historical order: {"owner": "prestashop_order_history_user@example.com", "reference": "PS-HISTORY-001", "date": "2026-07-18", "status": "Delivered", "product": "Hummingbird order-history t-shirt", "quantity": 1, "product_amount": 29, "shipping": 5, "total": 34, "address": "1 Commerce Road, Shanghai 200000, China", "payment": "Bank wire", "invoice": "Downloadable PDF for PS-HISTORY-001"}
    - **When:** Activate Details within PS-HISTORY-001.
    - **Then:** Order details identifies that reference and Hummingbird order-history t-shirt with its historical shipping address and Bank wire payment.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ORDER)`

### REQ-7.6 Reorder or download invoice

Within historical "PS-HISTORY-001"(role=row), "Reorder"(role=link) adds the available order-history t-shirt to Shopping cart with subtotal 29. "PDF"(role=link) downloads a valid invoice PDF for that reference, identified by its suggested filename. No internal order query is required.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-ORDER · account_orders**

![IMG-MY-ACCOUNT-ORDER · account_orders](reference/my_account_order.png)

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.6-01 — Reorder historical product
  - **Step:** STEP-REQ-7.6-01-01
    - **Given:** Signed-in order_history_user is viewing seeded PS-HISTORY-001 and its historical product remains available; the cart is empty.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-history t-shirt", "category": "Men", "price": 29, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_order_history_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - completed delivered historical order: {"owner": "prestashop_order_history_user@example.com", "reference": "PS-HISTORY-001", "date": "2026-07-18", "status": "Delivered", "product": "Hummingbird order-history t-shirt", "quantity": 1, "product_amount": 29, "shipping": 5, "total": 34, "address": "1 Commerce Road, Shanghai 200000, China", "payment": "Bank wire", "invoice": "Downloadable PDF for PS-HISTORY-001"}
    - **When:** Activate Reorder within that named order row.
    - **Then:** Shopping cart contains Hummingbird order-history t-shirt and subtotal 29.
    - **References:** `\ref[requirement](REQ-7.5)`, `\ref[requirement](REQ-3.3)`, `\ref[image](IMG-MY-ACCOUNT-ORDER)`, `\ref[image](IMG-CART)`
- SCN-REQ-7.6-02 — Download historical invoice
  - **Step:** STEP-REQ-7.6-02-01
    - **Given:** Signed-in order_history_user is viewing seeded PS-HISTORY-001.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_order_history_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - completed delivered historical order: {"owner": "prestashop_order_history_user@example.com", "reference": "PS-HISTORY-001", "date": "2026-07-18", "status": "Delivered", "product": "Hummingbird order-history t-shirt", "quantity": 1, "product_amount": 29, "shipping": 5, "total": 34, "address": "1 Commerce Road, Shanghai 200000, China", "payment": "Bank wire", "invoice": "Downloadable PDF for PS-HISTORY-001"}
    - **When:** Activate PDF within that order row and receive the browser download.
    - **Then:** The download succeeds, its suggested filename identifies PS-HISTORY-001 and ends in .pdf, and the downloaded bytes begin with %PDF-.
    - **References:** `\ref[requirement](REQ-7.5)`, `\ref[requirement](REQ-3.3)`, `\ref[image](IMG-MY-ACCOUNT-ORDER)`, `\ref[image](IMG-CART)`

### REQ-7.7 Create or inspect wishlists

"Wishlist"(role=link) opens saved collections, each represented by "{wishlist title}"(role=listitem) with a named opening entry and Edit and Delete actions. Clicking "Create new wishlist"(role=button) opens "Create new wishlist"(role=dialog), where "Name"(role=textbox) and "Save"(role=button) create exactly one Holiday Picks listitem. Favorites may similarly be created empty for rename and delete prerequisites. Opening seeded "Favorites"(role=link) shows its membership-bearing "Hummingbird wishlist t-shirt"(role=listitem) with Remove and Add to cart actions.

For wishlist with product membership: No source-defined authenticated flow adds products to a wishlist; seed only these membership-bearing Favorites objects. Rename/delete tests create an empty Favorites via the in-scope UI instead.

For empty wishlist: Created through REQ-7.7. Favorites and Holiday Picks are isolated to scenario-owned accounts.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-MY-ACCOUNT-WISHLIST · account_wishlists**

![IMG-MY-ACCOUNT-WISHLIST · account_wishlists](reference/my_account_wishlist.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.7-01 — Inspect seeded wishlist and products
  - **Step:** STEP-REQ-7.7-01-01
    - **Given:** Verified wishlist_view_user has seeded Favorites containing Hummingbird wishlist t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_view_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - wishlist with product membership: {"owners": ["prestashop_wishlist_view_user@example.com"], "name": "Favorites", "products": ["Hummingbird wishlist t-shirt"]}
    - **When:** Sign in, open Wishlist from My account, then activate Favorites.
    - **Then:** Favorites is visible in the collection list; opening it shows the named product listitem and its Add to cart action.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`
- SCN-REQ-7.7-02 — Create Holiday Picks wishlist
  - **Step:** STEP-REQ-7.7-02-01
    - **Given:** Signed-in wishlist_create_user has opened Wishlist.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_create_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Click Create new wishlist; enter Holiday Picks in Name within its dialog and click Save.
    - **Then:** Exactly one Holiday Picks collection appears with Edit and Delete actions.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`

### REQ-7.8 Rename or delete a wishlist

For wishlist_rename_user or wishlist_delete_user, the UI-created "Favorites"(role=listitem) offers scoped "Edit"(role=button) and "Delete"(role=button). Edit displays Favorites in "Name"(role=textbox); replacing it with Holiday Picks and clicking "Save"(role=button) leaves one Holiday Picks and no Favorites. Delete instead removes Favorites from the collection list.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-WISHLIST · account_wishlists**

![IMG-MY-ACCOUNT-WISHLIST · account_wishlists](reference/my_account_wishlist.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.8-01 — Rename Favorites wishlist
  - **Step:** STEP-REQ-7.8-01-01
    - **Given:** Signed-in wishlist_rename_user has created an empty Favorites collection through Create new wishlist.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_rename_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Click Edit within Favorites, verify Name contains Favorites, replace it with Holiday Picks and click Save.
    - **Then:** Favorites disappears and exactly one Holiday Picks collection remains.
    - **References:** `\ref[requirement](REQ-7.7)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`
- SCN-REQ-7.8-02 — Delete Favorites wishlist
  - **Step:** STEP-REQ-7.8-02-01
    - **Given:** Signed-in wishlist_delete_user has created an empty Favorites collection through Create new wishlist.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_delete_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Click Delete within Favorites and confirm deletion.
    - **Then:** Favorites is removed from the collection list.
    - **References:** `\ref[requirement](REQ-7.7)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`

### REQ-7.9 Remove wishlist product or move it to cart

Seeded Favorites for wishlist_remove_user or wishlist_cart_user contains "Hummingbird wishlist t-shirt"(role=listitem). "Remove"(role=button) deletes that product's wishlist membership; "Add to cart"(role=button) instead adds that exact default available product to the cart. If the wishlist remains visible after addition, "Cart"(role=link) opens the cart to inspect the selected product.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-WISHLIST · account_wishlists**

![IMG-MY-ACCOUNT-WISHLIST · account_wishlists](reference/my_account_wishlist.png)

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.9-01 — Remove Favorites product
  - **Step:** STEP-REQ-7.9-01-01
    - **Given:** Signed-in wishlist_remove_user has opened seeded Favorites containing Hummingbird wishlist t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_remove_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - wishlist with product membership: {"owners": ["prestashop_wishlist_remove_user@example.com"], "name": "Favorites", "products": ["Hummingbird wishlist t-shirt"]}
    - **When:** Click Remove within that product listitem.
    - **Then:** Hummingbird wishlist t-shirt is removed from Favorites.
    - **References:** `\ref[requirement](REQ-7.7)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`, `\ref[image](IMG-CART)`
- SCN-REQ-7.9-02 — Add Favorites product to cart
  - **Step:** STEP-REQ-7.9-02-01
    - **Given:** Signed-in wishlist_cart_user has opened seeded Favorites containing Hummingbird wishlist t-shirt and has an empty cart.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird wishlist t-shirt", "category": "Men", "price": 23, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_cart_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - wishlist with product membership: {"owners": ["prestashop_wishlist_cart_user@example.com"], "name": "Favorites", "products": ["Hummingbird wishlist t-shirt"]}
    - **When:** Click Add to cart within that product; wait for Cart to report one unit, dismiss an optional success dialog through Continue shopping, then activate Cart.
    - **Then:** Shopping cart contains the exact Hummingbird wishlist t-shirt product.
    - **References:** `\ref[requirement](REQ-7.7)`, `\ref[requirement](REQ-3.3)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`, `\ref[image](IMG-CART)`

### REQ-7.10 Delete only the selected address

After creating "Home"(role=article) and "Office"(role=article) through UI under the same account, clicking "Delete"(role=button) within Home removes only Home and preserves Office with its original values. Business identity, rather than row position, determines the target.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-ADDRESS · account_addresses**

![IMG-MY-ACCOUNT-ADDRESS · account_addresses](reference/my_account_address.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.10-01 — Delete only the selected address
  - **Step:** STEP-REQ-7.10-01-01
    - **Given:** Signed-in address_delete_user has created Home and Office through UI with 1 Commerce Road and 13800000020 and is viewing Addresses.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_address_delete_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
    - **When:** Click Delete within Home and confirm deletion.
    - **Then:** Home disappears; exactly one Office article remains with its original street and phone.
    - **References:** `\ref[requirement](REQ-7.3)`, `\ref[requirement](REQ-7.4)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`

### REQ-7.11 Delete only the selected wishlist

For UI-created "Favorites"(role=listitem) and "Holiday Picks"(role=listitem) under wishlist_delete_user, "Delete"(role=button) scoped to Favorites removes only that collection. Holiday Picks remains exactly once and its "Holiday Picks"(role=link) still opens the surviving wishlist with a Holiday Picks heading, independent of list ordering.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-MY-ACCOUNT-WISHLIST · account_wishlists**

![IMG-MY-ACCOUNT-WISHLIST · account_wishlists](reference/my_account_wishlist.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-7.11-01 — Delete only the selected wishlist
  - **Step:** STEP-REQ-7.11-01-01
    - **Given:** Signed-in wishlist_delete_user has created empty Favorites and Holiday Picks collections through UI.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_wishlist_delete_user@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
    - **When:** Click Delete within Favorites, confirm deletion, then activate the surviving Holiday Picks link.
    - **Then:** Favorites disappears, Holiday Picks remains exactly once, and its opening link displays the surviving wishlist.
    - **References:** `\ref[requirement](REQ-7.7)`, `\ref[requirement](REQ-7.8)`, `\ref[image](IMG-MY-ACCOUNT-WISHLIST)`
