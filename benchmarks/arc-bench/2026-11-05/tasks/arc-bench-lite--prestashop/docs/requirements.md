# PrestaShop B2C storefront

A B2C storefront for browsing products, selecting variants, managing a cart, completing checkout, signing in, and managing shipping addresses.

Displayed dates use UTC and the shared application/evaluator clock 2026-10-06T12:00:00Z.

For verified customers: The scenarios use existing verified customer accounts; account verification is outside scope. Address books start empty; UI setup creates Home where required. No initial account cart contains products.

For session, selected combination, cart and checkout state: Produced through the corresponding user interactions. Do not inject storage, cookies or API state.

## REQ-1 Storefront discovery

Support navigate categories and return home.

**Type:** FOLDER
**Dependencies:** None

### REQ-1.1 Navigate categories and return home

Hovering or keyboard-focusing and activating "CLOTHES"(role=link) reveals "Men"(role=link) and "Women"(role=link). Men opens its product listing with Hummingbird detail t-shirt and Sort by; activating CLOTHES itself opens the parent category. From any catalog page, "Logo"(role=link) returns home to Popular Products.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-NAVIGATION · home**

![IMG-NAVIGATION · home](reference/navigation.png)

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** None

**Scenarios:**

- SCN-REQ-1.1-01 — Browse Men and return with logo
  - **Step:** STEP-REQ-1.1-01-01
    - **Given:** The anonymous homepage is open and the seeded catalog contains Hummingbird detail t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}]}
    - **When:** Hover CLOTHES, activate Men, then activate Logo.
    - **Then:** Men initially shows its heading, Sort by and Hummingbird detail t-shirt; Logo returns to the homepage with Popular Products.
    - **References:** `\ref[image](IMG-NAVIGATION)`, `\ref[image](IMG-CATEGORY)`
- SCN-REQ-1.1-02 — Open subcategory by keyboard
  - **Step:** STEP-REQ-1.1-02-01
    - **Given:** The anonymous homepage is open.
    - **When:** Focus CLOTHES using the keyboard, press Enter to reveal its submenu, then focus Men and press Enter.
    - **Then:** Men opens with its heading and Hummingbird detail t-shirt in Product list.
    - **References:** `\ref[image](IMG-NAVIGATION)`, `\ref[image](IMG-CATEGORY)`

## REQ-2 Catalog exploration

Support inspect category listing and breadcrumb.

**Type:** FOLDER
**Dependencies:** None

### REQ-2.1 Inspect category listing and breadcrumb

Men displays its heading, Category description region containing Men, a numeric Product count status, Sort by combobox, and Product list region. Breadcrumb navigation shows Home, CLOTHES and Men in that order. Product list has a Product <name> region for each product and each product name opens its detail. Sale price and Regular price regions contain one USD amount with a decimal point. Catalog filters, pagination and sorting behavior are outside scope.

**IMG-CATEGORY · category**

![IMG-CATEGORY · category](reference/category.png)

**Type:** ATOMIC
**Dependencies:** REQ-1.1

**Scenarios:**

- SCN-REQ-2.1-01 — Inspect category and breadcrumb
  - **Step:** STEP-REQ-2.1-01-01
    - **Given:** The seeded catalog is available to an anonymous visitor.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}, {"name": "Hummingbird cart t-shirt", "category": "Men", "price": 25, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}, {"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "categories": {"CLOTHES": ["Men", "Women"], "ACCESSORIES": [], "ART": []}, "men_page_size": 12}
    - **When:** Open CLOTHES then Men through Global navigation.
    - **Then:** Men heading, Category description, numeric Product count, Sort by and Product list are visible; Breadcrumb presents Home, CLOTHES and Men in that order.
    - **References:** `\ref[image](IMG-CATEGORY)`

## REQ-3 Product selection

Support inspect product details, select product combination and quantity, add product to cart and choose next destination, update price and stock for selected variant.

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
**Dependencies:** REQ-2.1

**Scenarios:**

- SCN-REQ-3.1-01 — Inspect selected product
  - **Step:** STEP-REQ-3.1-01-01
    - **Given:** The seeded Hummingbird detail t-shirt is available in Men.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "tax_rate": 0.2, "detail_images": [{"identity": "Front", "description": "Front view of Hummingbird detail t-shirt"}, {"identity": "Back", "description": "Back view of Hummingbird detail t-shirt"}]}
    - **When:** Open its named product link and inspect Product images and Product information.
    - **Then:** The detail heading and Add to cart identify the product; exactly one main image has its product name, thumbnails and Zoom are available, and information shows sale price 24, regular price 30, 20% discount, tax and regular-fit description.
    - **References:** `\ref[image](IMG-CATEGORY)`, `\ref[image](IMG-PRODUCT-DETAIL)`

### REQ-3.2 Select product combination and quantity

Users choose M in "Size"(role=combobox) and "White"(role=radio), with price and stock reflecting that combination. "Quantity"(role=spinbutton) starts at 1; "Increase quantity"(role=button) changes it to 2, while "Decrease quantity"(role=button) returns it to 1 and cannot reduce it below 1. Direct entry of 3 is accepted. Entering 999 exceeds stock, so "Add to cart"(role=button) shows an insufficient-stock alert and adds no product.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.1

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
**Dependencies:** REQ-3.2

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

### REQ-3.4 Update price and stock for selected variant

Choosing L in "Size"(role=combobox) and "Black"(role=radio) updates "Product information"(role=region) to the published catalog variant's sale price 36, regular price 45, and "Stock"(role=status) displaying Available stock: 2. Selecting M and "White"(role=radio) restores sale price 24, regular price 30, and Available stock: 50. Both monetary values and stock must follow the actual selected combination rather than only changing the selection controls.

Product information exposes named Sale price and Regular price amounts. Stock status displays "Available stock: <number>". Selected product and variant remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

**IMG-PRODUCT-DETAIL · product**

![IMG-PRODUCT-DETAIL · product](reference/product_detail.png)

**Type:** ATOMIC
**Dependencies:** REQ-3.2

**Scenarios:**

- SCN-REQ-3.4-01 — Update price and stock for selected variant
  - **Step:** STEP-REQ-3.4-01-01
    - **Given:** Hummingbird detail t-shirt detail is open with the catalog variant data.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Select L in Size and Black (radio), inspect information, then select M and White (radio).
    - **Then:** L/Black shows sale price 36, regular price 45 and Available stock: 2; M/White restores price 24, regular price 30 and Available stock: 50.
    - **References:** `\ref[requirement](REQ-3.2)`, `\ref[image](IMG-PRODUCT-DETAIL)`

## REQ-4 Cart management

Support inspect cart contents and summary, change or remove cart items, continue browsing or begin checkout, edit cart quantity directly, carry selected variant into cart.

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
**Dependencies:** REQ-3.3

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
**Dependencies:** REQ-4.1

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
**Dependencies:** REQ-4.1

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
**Dependencies:** REQ-4.1

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
**Dependencies:** REQ-3.4, REQ-4.1

**Scenarios:**

- SCN-REQ-4.5-01 — Carry selected variant into cart
  - **Step:** STEP-REQ-4.5-01-01
    - **Given:** Hummingbird detail t-shirt detail is open with an empty cart; L/Black has stock 2 and sale/regular prices 36/45.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird detail t-shirt", "category": "Men", "price": 24, "regular_price": 30, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Cotton", "brand": "Hummingbird"}], "tax_rate": 0.2, "detail_variants": [{"size": "M", "color": "White", "price": 24, "regular_price": 30, "stock": 50}, {"size": "L", "color": "Black", "price": 36, "regular_price": 45, "stock": 2}]}
    - **When:** Select L and Black, enter Quantity 2, click Add to cart and use Proceed to checkout in the success dialog.
    - **Then:** The cart row retains L/Black and quantity 2 at unit price 36; Items subtotal is 72, Shipping 5, informational Discount 18 and Total 77, without deducting the discount again.
    - **References:** `\ref[requirement](REQ-3.4)`, `\ref[requirement](REQ-4.1)`, `\ref[image](IMG-PRODUCT-DETAIL)`, `\ref[image](IMG-CART)`

## REQ-5 Checkout completion

Support start checkout and inspect customer information, select shipping address, separate invoice address and choose carrier, choose payment and read terms, place order and inspect completion.

**Type:** FOLDER
**Dependencies:** None

### REQ-5.1 Start checkout and inspect customer information

Anonymous checkout with the checkout-step t-shirt opens "Personal Information"(role=region) and "Order summary"(role=region). For signed-in checkout_user, Personal Information displays the case-isolated email declared for prestashop_checkout_user@example.com; its "Continue"(role=button) opens "Addresses"(role=region) if that step is not already active.

Anonymous checkout exposes login, registration, or guest-information entry. Concrete guest completion is unspecified.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CART · cart**

![IMG-CART · cart](reference/cart.png)

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**Type:** ATOMIC
**Dependencies:** REQ-4.3, REQ-6.1, REQ-7.2

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
      - verified customers: {"accounts": [{"email": "prestashop_checkout_user+fb1a31620f@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
      Scenario account identities: {"prestashop_checkout_user@example.com": "prestashop_checkout_user+fb1a31620f@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Proceed from Shopping cart into checkout; inspect Personal Information and click its Continue if Addresses is not already active.
    - **Then:** Personal Information identifies prestashop_checkout_user+fb1a31620f@example.com and Addresses offers Home without losing the order product.
    - **References:** `\ref[requirement](REQ-4.3)`, `\ref[requirement](REQ-7.2)`, `\ref[image](IMG-CART)`, `\ref[image](IMG-CHECKOUT)`

### REQ-5.2 Select shipping address

After checkout_address_user creates Home through UI, "Addresses"(role=region) offers "Home"(role=radio) with 1 Commerce Road. Selecting it visibly marks that address; "Continue"(role=button) progresses to Shipping Method while retaining the same order product.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-ADDRESS · checkout**

![IMG-CHECKOUT-ADDRESS · checkout](reference/checkout_address.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.1, REQ-7.2

**Scenarios:**

- SCN-REQ-5.2-01 — Select Home address
  - **Step:** STEP-REQ-5.2-01-01
    - **Given:** Signed-in checkout_address_user has created Home at 1 Commerce Road through UI and entered Addresses with one Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_address_user+0cf6a33136@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_cost": 5}
      Scenario account identities: {"prestashop_checkout_address_user@example.com": "prestashop_checkout_address_user+0cf6a33136@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Select Home (radio), inspect its checked state and street, then click Continue within Addresses.
    - **Then:** Home is visibly selected with 1 Commerce Road; Shipping Method opens and Order summary retains the selected product.
    - **References:** `\ref[requirement](REQ-5.1)`, `\ref[requirement](REQ-7.2)`, `\ref[image](IMG-CHECKOUT-ADDRESS)`

### REQ-5.3 Separate invoice address and choose carrier

With checkout_invoice_user's UI-created Home available, clearing "Use same address"(role=checkbox) reveals "Invoice address"(role=region), including Home. Continuing with Home opens "Shipping Method"(role=region), where "Delivery"(role=radio) displays cost 5 and visibly reflects selection. "Order summary"(role=region) includes the checkout-step t-shirt price 26 plus shipping 5, totaling 31.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-SHIPPING · checkout**

![IMG-CHECKOUT-SHIPPING · checkout](reference/checkout_shipping.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.2

**Scenarios:**

- SCN-REQ-5.3-01 — Use separate invoice address
  - **Step:** STEP-REQ-5.3-01-01
    - **Given:** Signed-in checkout_invoice_user has created Home through UI and is at Addresses with Hummingbird checkout-step t-shirt.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user+93d52df5e1@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
      Scenario account identities: {"prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+93d52df5e1@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Uncheck Use same address (checkbox).
    - **Then:** Invoice address appears and includes Home as an available billing address.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT-SHIPPING)`
- SCN-REQ-5.3-02 — Choose Delivery
  - **Step:** STEP-REQ-5.3-02-01
    - **Given:** Signed-in checkout_invoice_user has created Home through UI and reached Addresses with Hummingbird checkout-step t-shirt priced 26.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user+749408dfcd@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5}
      Scenario account identities: {"prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+749408dfcd@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Select Home, click Continue in Addresses, then select Delivery (radio) in Shipping Method.
    - **Then:** Delivery is checked with cost 5; Order summary retains the product and shows total 31.
    - **References:** `\ref[requirement](REQ-5.2)`, `\ref[image](IMG-CHECKOUT-SHIPPING)`

### REQ-5.4 Choose payment and read terms

Continuing after Delivery selection opens "Payment"(role=region), where users select "Bank wire"(role=radio) and agree through "Terms and conditions"(role=checkbox). The separate "Terms and conditions"(role=link) opens "Terms and conditions"(role=region) with agreement content. "Place order"(role=button) completes the order only after agreement.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT-PAYMENT · checkout**

![IMG-CHECKOUT-PAYMENT · checkout](reference/checkout_payment.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.3

**Scenarios:**

- SCN-REQ-5.4-01 — Choose bank wire and read terms
  - **Step:** STEP-REQ-5.4-01-01
    - **Given:** A signed-in checkout customer has created Home, added Hummingbird checkout-step t-shirt, completed Home and Delivery, and reached Payment.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user+2ca94350c4@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
      Scenario account identities: {"prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+2ca94350c4@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Select Bank wire (radio), check Terms and conditions (checkbox), then activate the separate Terms and conditions link.
    - **Then:** Bank wire and agreement are selected; the Terms and conditions region displays agreement content.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-CHECKOUT-PAYMENT)`
- SCN-REQ-5.4-02 — Require terms before completion
  - **Step:** STEP-REQ-5.4-02-01
    - **Given:** The signed-in customer has reached Payment with Home and Delivery completed and Hummingbird checkout-step t-shirt retained.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird checkout-step t-shirt", "category": "Men", "price": 26, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_invoice_user+2f48453359@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
      Scenario account identities: {"prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+2f48453359@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Select Bank wire, leave Terms and conditions unchecked, and attempt Place order if the action is enabled.
    - **Then:** Order confirmation is not displayed; the product remains in Order summary and agreement is still required, whether Place order is disabled or the attempt is rejected.
    - **References:** `\ref[requirement](REQ-5.3)`, `\ref[image](IMG-CHECKOUT-PAYMENT)`

### REQ-5.5 Place order and inspect completion

Using checkout_6_6_user with the order-confirmation t-shirt or checkout_6_7_user with the order-complete t-shirt, users complete Home, Delivery, Bank wire, and agreement, then click "Place order"(role=button). Order confirmation displays the chosen product; "Order reference"(role=region) contains a nonempty assigned reference, and "Order details"(role=region) shows product, quantity, amounts, shipping, and payment. "Continue shopping"(role=link) returns home with Search, My account, and Cart.

Order summary and checkout steps Personal Information, Addresses, Shipping Method, and Payment are named regions. Continue actions are scoped to their step. Expanded steps expose inputs; completed collapsed steps expose summaries and edit actions and hide completed inputs. Shipping cost is a named amount region. Step data remain consistent across navigation within a flow.

Order details identifies "Quantity: <value>".

For new order: Created through REQ-5.5; assigned reference is observed, never predetermined.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

Checkout steps Personal Information, Addresses, Shipping Method and Payment, and Order summary, are named regions. Continue is scoped to its step; completed collapsed steps show summaries/edit actions and hide their completed inputs. Data remain consistent when editing and reopening a completed step.

**IMG-CHECKOUT · checkout**

![IMG-CHECKOUT · checkout](reference/checkout.png)

**IMG-CHECKOUT-SUMMARY · order_confirmation**

![IMG-CHECKOUT-SUMMARY · order_confirmation](reference/checkout_summary.png)

**Type:** ATOMIC
**Dependencies:** REQ-5.4

**Scenarios:**

- SCN-REQ-5.5-01 — Place order for selected product
  - **Step:** STEP-REQ-5.5-01-01
    - **Given:** Signed-in checkout_6_6_user has created Home and added one Hummingbird order-confirmation t-shirt through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-confirmation t-shirt", "category": "Men", "price": 27, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}]}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_6_6_user+a7a2c7bd17@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
      Scenario account identities: {"prestashop_checkout_6_6_user@example.com": "prestashop_checkout_6_6_user+a7a2c7bd17@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Proceed to checkout, select Home and continue, select Delivery and continue, select Bank wire, check Terms and conditions, then click Place order.
    - **Then:** Order confirmation opens and identifies Hummingbird order-confirmation t-shirt.
    - **References:** `\ref[requirement](REQ-5.4)`, `\ref[image](IMG-CHECKOUT)`, `\ref[image](IMG-CHECKOUT-SUMMARY)`
- SCN-REQ-5.5-02 — Inspect completed order and continue shopping
  - **Step:** STEP-REQ-5.5-02-01
    - **Given:** Signed-in checkout_6_7_user has created Home and added one Hummingbird order-complete t-shirt through UI.
      Seed prerequisites (prepared before this scenario):
      - published catalog: {"currency": "USD", "products": [{"name": "Hummingbird order-complete t-shirt", "category": "Men", "price": 28, "regular_price": null, "stock": 50, "color": "White", "size": "M", "purchasable": true, "composition": "Polyester", "brand": "Hummingbird"}], "tax_rate": 0.2}
      - verified customers: {"accounts": [{"email": "prestashop_checkout_6_7_user+1c994d0506@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"], "shipping_method": "Delivery", "shipping_cost": 5, "payment_method": "Bank wire", "terms": "Terms and conditions"}
      Scenario account identities: {"prestashop_checkout_6_7_user@example.com": "prestashop_checkout_6_7_user+1c994d0506@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Complete checkout with Home, Delivery, Bank wire and checked Terms and conditions; click Place order, inspect confirmation, then activate Continue shopping.
    - **Then:** Confirmation has a nonempty Order reference; Order details shows the product, quantity 1, total 33, Home, Delivery and Bank wire. Continue shopping returns home with Search, My account and Cart available.
    - **References:** `\ref[requirement](REQ-5.4)`, `\ref[image](IMG-CHECKOUT)`, `\ref[image](IMG-CHECKOUT-SUMMARY)`

## REQ-6 Customer access

Support sign in with password visibility and remember option.

**Type:** FOLDER
**Dependencies:** None

### REQ-6.1 Sign in with password visibility and remember option

Clicking "Sign in"(role=button) opens "Email"(role=textbox), masked "Password"(role=textbox), a Sign in submit action. "SHOW"(role=button) reveals the password and "Remember me"(role=checkbox) is selectable. Valid verified Store User credentials sign in, showing Store User, "My account"(role=link), and "Sign out"(role=button). Registration does not replace the source's verified-account fixture.

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
      - verified customers: {"accounts": [{"email": "prestashop_user+b389cfbdfd@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      Scenario account identities: {"prestashop_user@example.com": "prestashop_user+b389cfbdfd@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Enter those credentials, click SHOW, check Remember me, then click the Sign in submit button.
    - **Then:** Email retains its value, Password becomes visible with the entered value, Remember me is checked, and successful sign-in exposes Store User, My account and Sign out in Global navigation.
    - **References:** `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-LOGIN)`, `\ref[image](IMG-MY-ACCOUNT)`

## REQ-7 Account management

Support inspect account overview, create and view addresses.

**Type:** FOLDER
**Dependencies:** None

### REQ-7.1 Inspect account overview

My account after login opens the My account heading and Account overview region showing Store User and the Addresses entry. Addresses leads to the retained address creation flow. Profile changes, wishlists and historical order management are outside scope.

**IMG-HOMEPAGE · home**

![IMG-HOMEPAGE · home](reference/homepage.png)

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**Type:** ATOMIC
**Dependencies:** REQ-6.1

**Scenarios:**

- SCN-REQ-7.1-01 — Inspect account overview
  - **Step:** STEP-REQ-7.1-01-01
    - **Given:** Verified Store User has signed in through Email and Password.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user+9dfc67df54@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      Scenario account identities: {"prestashop_user@example.com": "prestashop_user+9dfc67df54@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Activate My account (link).
    - **Then:** My account heading and Account overview show Store User and an Addresses entry.
    - **References:** `\ref[requirement](REQ-6.1)`, `\ref[image](IMG-HOMEPAGE)`, `\ref[image](IMG-MY-ACCOUNT)`

### REQ-7.2 Create and view addresses

Clicking "Addresses"(role=link) displays each saved address as "{alias}"(role=article), containing its values and Update and Delete actions. "Create new address"(role=button) opens "Alias"(role=textbox), "First name"(role=textbox), "Last name"(role=textbox), "Address"(role=textbox), "Postal code"(role=textbox), "City"(role=textbox), "Country"(role=combobox), and "Phone"(role=textbox), displaying entered values before submission. "Save"(role=button) with Office and shared examples address values creates one Office article; Home setup uses the same creation behavior and values.

For customer address: Created through REQ-7.2. Home/Office: Store User, 1 Commerce Road, 200000, Shanghai, China, 13800000020. Home is created in UI setup before selection/edit/delete scenarios. Updated street: 88 Market Street.

English action names are case-insensitive. Global navigation remains available across pages; each mutation affects the selected business identity.

The existing customer address books start empty. Home is created through the address UI before address selection, editing or deletion; it is not an extra preloaded address.

**IMG-MY-ACCOUNT · account**

![IMG-MY-ACCOUNT · account](reference/my_account.png)

**IMG-MY-ACCOUNT-ADDRESS · account_addresses**

![IMG-MY-ACCOUNT-ADDRESS · account_addresses](reference/my_account_address.png)

**Type:** ATOMIC
**Dependencies:** REQ-7.1

**Scenarios:**

- SCN-REQ-7.2-01 — View Home address
  - **Step:** STEP-REQ-7.2-01-01
    - **Given:** Signed-in address_view_user has created Home through the normal address UI using Store User, 1 Commerce Road, 200000 Shanghai, China and 13800000020.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user+c9e12a333b@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}, {"email": "prestashop_address_view_user+c9e12a333b@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
      Scenario account identities: {"prestashop_user@example.com": "prestashop_user+c9e12a333b@example.com", "prestashop_address_view_user@example.com": "prestashop_address_view_user+c9e12a333b@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Open Addresses from Account overview.
    - **Then:** Home (article) shows those saved values and its Update and Delete actions.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`
- SCN-REQ-7.2-02 — Create Office address
  - **Step:** STEP-REQ-7.2-02-01
    - **Given:** Signed-in address_create_user has opened Addresses and has no address articles.
      Seed prerequisites (prepared before this scenario):
      - verified customers: {"accounts": [{"email": "prestashop_user+e4b0ed97e7@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}, {"email": "prestashop_address_create_user+e4b0ed97e7@example.com", "password": "ShopPass123!", "first_name": "Store", "last_name": "User", "birthdate": "1995-08-21"}]}
      - available fulfillment choices: {"countries": ["China"]}
      Scenario account identities: {"prestashop_user@example.com": "prestashop_user+e4b0ed97e7@example.com", "prestashop_address_create_user@example.com": "prestashop_address_create_user+e4b0ed97e7@example.com"}. Use the declared login identity; public display/holder names remain unchanged. Each scenario account starts with no additional passengers/current orders (12306) or an empty cart and address book (PrestaShop).
    - **When:** Click Create new address; enter Alias Office, First name Store, Last name User, Address 1 Commerce Road, Postal code 200000, City Shanghai, Country China and Phone 13800000020; inspect entered values, then click Save.
    - **Then:** Exactly one Office article displays the saved address values with Update and Delete controls.
    - **References:** `\ref[requirement](REQ-7.1)`, `\ref[image](IMG-MY-ACCOUNT)`, `\ref[image](IMG-MY-ACCOUNT-ADDRESS)`
