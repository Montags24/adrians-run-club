import requests

URL = "https://api.runrepeat.com/get-documents"

# Create dictionary that stores key:value pairs of shoe size to headers used in RunRepeat's API
sizes = {
    6: 1704,
    6.5: 1705,
    7: 1706,
    7.5: 1707,
    8: 1708,
    8.5: 1709,
    9: 1710,
    9.5: 1711,
    10: 1712,
    10.5: 1713,
    11: 1714,
    11.5: 1715,
    12: 1716,
    12.5: 1717,
    13: 1718,
}


def change_parameters(size, page, page_range):
    size_parameters = {
        "from": page_range,
        "size": 30,
        "filter[]": [1, 6214, 16078, sizes[size]],
        "f_id": 2,
        "c_id": 2,
        "orderBy": "popularity",
        "page_gender": "false",
        "event": {"type": "pagination", "value": page},
    }
    return size_parameters


def retrieve_data():
    """Function that uses RunRepeat API to return data on competitive running shoes"""
    shoe_data = []
    for size in sizes:
        # Run loop 3 times to get up to 90 shoes worth of data
        for i in range(3):
            parameters = change_parameters(size, i + 1, 30 * i)
            response = requests.get(URL, params=parameters)
            data = response.json()
            for product in data["products"]:
                shoe_data.append(
                    [product["name"], f"{size}", {
                        "price": product["msrp"],
                        "discount": product["min_price"],
                        "score": product["score"],
                        "img_link": product["default_color"]["image"]["url"].replace("{SIZE}", "600"),
                        "deal_link": product["deals"][0]["affiliate_link"]
                    }
                    ]
                )
    return shoe_data
