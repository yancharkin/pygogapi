class SearchResult:
    def __init__(self, api, query, search_data):
        self.api = api
        self.query = query
        self.load_search(search_data)

    def load_search(self, search_data):
        self.products = []
        for product_data in search_data["products"]:
            product = self.api.get_product(product_data["id"])
            prod.load_gog_min(product_data)
            products.append(product)

        self.page = int(search_data["page"])
        self.total_pages = search_data["totalPages"]
        self.total_results = int(search_data["totalResults"])
        self.total_games_found = search_data["totalGamesFound"]
        self.total_movies_found = search_data["totalMoviesFound"]

    def next_page(self):
        assert self.page < self.total_pages
        new_query = self.query.copy()
        new_query["page"] = self.page + 1
        return self.api.search(new_query)

    def previous_page(self):
        assert self.page > 0
        new_query = self.query.copy()
        new_query["page"] = self.page - 1
        return self.api.search(new_query)