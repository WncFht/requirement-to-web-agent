export const PASS = "Password123!";
export const trains = [
    {
        "number": "G1001",
        "from_station": "Shanghai Hongqiao",
        "to_station": "Beijing South",
        "departure": "08:00",
        "arrival": "13:00",
        "duration": 300,
        "second_price": 576
    },
    {
        "number": "G1002",
        "from_station": "Shanghai",
        "to_station": "Beijing",
        "departure": "13:00",
        "arrival": "19:00",
        "duration": 360,
        "second_price": 600
    },
    {
        "number": "K1003",
        "from_station": "Shanghai",
        "to_station": "Beijing South",
        "departure": "00:30",
        "arrival": "15:30",
        "duration": 900,
        "second_price": 200
    }
] as const;
