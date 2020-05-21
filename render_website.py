import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
import math
from urllib.parse import quote
import glob
import os


def get_books_from_json(filename):
    with open(filename, 'r') as books_json:
        books = json.loads(books_json.read())

    return books


def clean_pages_files(exists_pages_nums, pages_dir='pages'):
    all_pages = glob.glob(f"{pages_dir}/*.html")

    for page in all_pages:
        page_number = page.split('/')[-1].split('.')[0]

        if int(page_number) not in exists_pages_nums:
            os.remove(page)


def on_reload():
    exists_pages = set()

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

        with open(f'pages/{num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
            exists_pages = exists_pages | {num}

    clean_pages_files(exists_pages)


if __name__ == '__main__':
    template_file = 'template.html'

    on_reload()
    server = Server()
    server.watch(template_file, on_reload)
    server.serve(root='.')
