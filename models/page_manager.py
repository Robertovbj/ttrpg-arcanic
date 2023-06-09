class PageManager:
    def __init__(self, title, pages, description=None, thumbnail=None):
        self.title = title
        self.description = description
        self.color = 0xff3838
        self.pages = pages
        self.thumbnail = thumbnail
        self.current_page_index = 0

    def add_page(self, page):
        self.pages.append(page)

    def get_current_page(self):
        return self.pages[self.current_page_index]
    
    def get_current_page_index(self):
        return self.current_page_index
    
    def get_pages_amount(self):
        return len(self.pages)

    def get_embed_dict(self):
        current_page = self.get_current_page()
        manager_dict = {
            'title': self.title,
            'description': self.description,
            'color': self.color,
            'thumbnail': {
                'url': self.thumbnail
            },
            'footer': {
                'text': f'Page {self.current_page_index + 1} of {len(self.pages)}'
            }
        }
        return {**manager_dict, **current_page.to_dict()}

    def turn_page(self, delta):
        self.current_page_index += delta
        if self.current_page_index < 0:
            self.current_page_index = len(self.pages) - 1
        elif self.current_page_index >= len(self.pages):
            self.current_page_index = 0