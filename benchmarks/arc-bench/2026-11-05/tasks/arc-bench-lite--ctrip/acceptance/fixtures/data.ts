export const BENCHMARK_NOW = "2026-07-19T08:00:00+08:00";
export const IDS = ["110101199001011237", "110101199001021232", "110101199001031238"];
export const ACCOUNTS: Record<string, { email: string; password: string; [key: string]: unknown }> = {
  "user": {
    "email": "ctrip_user@example.com",
    "password": "Travel1234",
    "username": "ctrip_user",
    "mobile": "13800000010"
  },
  "order_read": {
    "email": "ctrip_order_read@example.com",
    "password": "Travel1234"
  },
  "order_cancel": {
    "email": "ctrip_order_cancel@example.com",
    "password": "Travel1234"
  },
  "profile_read": {
    "email": "ctrip_profile_read@example.com",
    "password": "Travel1234"
  }
};
