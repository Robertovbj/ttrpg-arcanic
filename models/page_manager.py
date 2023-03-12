from .page import Page

class PageManager:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages
        self.current_page_index = 0

    def add_page(self, page):
        self.pages.append(page)

    def get_current_page(self):
        return self.pages[self.current_page_index]
    
    def get_current_page_index(self):
        return self.current_page_index

    def get_embed_dict(self):
        current_page = self.get_current_page()
        return {
            'title': self.title,
            'description': current_page.description,
            'fields': current_page.fields
        }

    def turn_page(self, delta):
        self.current_page_index += delta
        if self.current_page_index < 0:
            self.current_page_index = len(self.pages) - 1
        elif self.current_page_index >= len(self.pages):
            self.current_page_index = 0