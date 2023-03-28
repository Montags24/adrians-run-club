import requests

URL = "https://api.runrepeat.com/get-documents"
# Create dictionary that stores key:value pairs of shoe size to headers used in RunRepeat's API
# UK sizes
min_size = 6
max_size = 13.5
run_repeat_start_size = 1698 + min_size
sizes = {size * 0.5: run_repeat_start_size + i for i, size in enumerate(range(min_size * 2, int(max_size * 2)))}


def change_parameters(size, page, page_range):
    size_parameters = {
        "from": page_range,
        "size": 30,
        "filter[]": [1, 6214, 16078, sizes[size]],  # 6214 - Running shoes, 16078 Competition running shoes
        "f_id": 2,
        "c_id": 2,
        "orderBy": "popularity",
        "page_gender": "false",
        "event": {"type": "pagination", "value": page},
    }
    return size_parameters


def retrieve_data(region):
    """Function that uses RunRepeat API to return data on competitive running shoes"""
    shoe_data = []
    headers = {"rr-country": region}
    for size in sizes:
        # Run loop 3 times to get up to 90 shoes worth of data
        for i in range(3):
            parameters = change_parameters(size, i + 1, 30 * i)
            response = requests.get(URL, headers=headers, params=parameters)
            data = response.json()
            for product in data["products"]:
                for deal in product["deals"]:
                    shoe_descriptor = deal["color"]["name"].split(" - ")
                    name = shoe_descriptor[0]
                    colour = shoe_descriptor[1].split(" (")[0]
                    shoe_data.append(
                        {
                            "name": name,
                            "colour": colour,
                            "size": size,
                            "price": product["msrp"],
                            "discount": deal["price_local"],
                            "country": region,
                            "score": product["score"],
                            "img_link": deal["color"]["image"]["url"].replace("{SIZE}", "600"),
                            "deal_link": deal["affiliate_link"]
                        }
                    )
    return shoe_data
