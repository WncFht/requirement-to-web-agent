// Public case-isolated SEED identities, declared in requirements.yaml.
const accounts: Record<string, Record<string, string>> = {
  "REQ-5.1: Inspect signed-in customer": {
    "prestashop_checkout_user@example.com": "prestashop_checkout_user+fb1a31620f@example.com"
  },
  "REQ-5.2: Select Home address": {
    "prestashop_checkout_address_user@example.com": "prestashop_checkout_address_user+0cf6a33136@example.com"
  },
  "REQ-5.3: Use separate invoice address": {
    "prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+93d52df5e1@example.com"
  },
  "REQ-5.3: Choose Delivery": {
    "prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+749408dfcd@example.com"
  },
  "REQ-5.4: Choose bank wire and read terms": {
    "prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+2ca94350c4@example.com"
  },
  "REQ-5.4: Require terms before completion": {
    "prestashop_checkout_invoice_user@example.com": "prestashop_checkout_invoice_user+2f48453359@example.com"
  },
  "REQ-5.5: Place order for selected product": {
    "prestashop_checkout_6_6_user@example.com": "prestashop_checkout_6_6_user+a7a2c7bd17@example.com"
  },
  "REQ-5.5: Inspect completed order and continue shopping": {
    "prestashop_checkout_6_7_user@example.com": "prestashop_checkout_6_7_user+1c994d0506@example.com"
  },
  "REQ-6.1: Reveal password and sign in": {
    "prestashop_user@example.com": "prestashop_user+b389cfbdfd@example.com"
  },
  "REQ-7.1: Inspect account overview": {
    "prestashop_user@example.com": "prestashop_user+9dfc67df54@example.com"
  },
  "REQ-7.2: View Home address": {
    "prestashop_user@example.com": "prestashop_user+c9e12a333b@example.com",
    "prestashop_address_view_user@example.com": "prestashop_address_view_user+c9e12a333b@example.com"
  },
  "REQ-7.2: Create Office address": {
    "prestashop_user@example.com": "prestashop_user+e4b0ed97e7@example.com",
    "prestashop_address_create_user@example.com": "prestashop_address_create_user+e4b0ed97e7@example.com"
  }
};
export function accountForCase(identity: string, title: string): string {
  return accounts[title]?.[identity] ?? identity;
}
