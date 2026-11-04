// Public case-isolated SEED identities, declared in requirements.yaml.
const accounts: Record<string, Record<string, string>> = {
  "REQ-3.1.1: Open authenticated personal center": {
    "personal_center_user": "personal_center_user__e029177424"
  },
  "REQ-3.1.2: Enter authenticated personal center": {
    "personal_center_user": "personal_center_user__d33ca86e66"
  },
  "REQ-3.2.1: Open ticket-order categories": {
    "orders_empty_user": "orders_empty_user__541dccecc4"
  },
  "REQ-3.3.1: Open unpaid-order view": {
    "orders_unpaid_user": "orders_unpaid_user__1ec57c26f1"
  },
  "REQ-3.3.2: Inspect unpaid order table": {
    "orders_unpaid_user": "orders_unpaid_user__c80b5ef98a"
  },
  "REQ-3.3.3: Resume payment by order identity": {
    "orders_unpaid_user": "orders_unpaid_user__ce3450b1ce"
  },
  "REQ-4.1: Inspect passenger table and protected holder": {
    "passenger_manager_user": "passenger_manager_user__9b2228b8b5"
  },
  "REQ-4.2: Add passenger with durable identity": {
    "passenger_manager_user": "passenger_manager_user__437d22ac41"
  },
  "REQ-4.2: Reject empty passenger form": {
    "passenger_manager_user": "passenger_manager_user__7354fa00f1"
  },
  "REQ-4.2: Reject duplicate passenger passport": {
    "passenger_manager_user": "passenger_manager_user__19b9a02304"
  },
  "REQ-4.2: Reject passenger invalid email": {
    "passenger_manager_user": "passenger_manager_user__e331852628"
  },
  "REQ-5.1.1: Open selected-journey booking form": {
    "bookable_user": "bookable_user__ec2ffd4821"
  },
  "REQ-5.1.2: Inspect selected train and availability": {
    "bookable_user": "bookable_user__ba2ce8567c"
  },
  "REQ-5.1.3.1: Select and configure booking passenger": {
    "bookable_user": "bookable_user__e4fc0022c2"
  },
  "REQ-5.2.1: Open booking confirmation state": {
    "booking_submit_user": "booking_submit_user__7f1c07ba54"
  },
  "REQ-5.2.2: Open confirmation for available seat": {
    "booking_submit_user": "booking_submit_user__f267665a01"
  },
  "REQ-5.2.2: Reject no passenger": {
    "bookable_user": "bookable_user__b227b3ca77"
  },
  "REQ-5.2.2: Reject unavailable ticket class": {
    "bookable_user": "bookable_user__3ad263d181"
  },
  "REQ-5.2.3.1: Confirm order and reach payment": {
    "booking_confirm_user": "booking_confirm_user__3b5cb6c2e7"
  },
  "REQ-5.2.3.2: Edit without submitting": {
    "booking_edit_user": "booking_edit_user__ffcd06ee2e"
  },
  "REQ-5.3: Show consistent payment and running countdown": {
    "booking_payment_user": "booking_payment_user__c688a2b321"
  },
  "REQ-5.4: Pay and persist upcoming state": {
    "booking_paid_user": "booking_paid_user__ee27938bcc"
  },
  "REQ-5.5: Persist unpaid order category": {
    "booking_unpaid_user": "booking_unpaid_user__c217ceeb2c"
  }
};
export function accountForCase(identity: string, title: string): string {
  return accounts[title]?.[identity] ?? identity;
}
