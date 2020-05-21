import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import math
from urllib.parse import quote


def get_books_from_json(filename):
    with open(filename, 'r') as books_json:
        books = json.loads(books_json.read())

    return books


def on_reload():
    books = get_books_from_json('books.json')
    books_per_page = 15
    total_pages = math.ceil(len(books) / books_per_page)

    for book in books:
        current_book_path = book['book_path']
        book['book_path'] = quote(current_book_path)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    chunked_books = chunked(books, books_per_page)
    for num, chunk_books in enumerate(chunked_books, start=1):

        rendered_page = template.render(
            total_pages=total_pages,
            current_page=num,
            books=chunked(chunk_books, 2)
        )

        with open(f'dist/index{num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    template_file = 'template.html'

    on_reload()
    server = Server()
    server.watch(template_file, on_reload)
    server.serve(root='.')
