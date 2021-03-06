from sqliteDB import SqliteDB
from plyer import filechooser
from shutil import copyfile
from PIL import Image
from random import randint
import re
import os.path
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import defaultdict
import itertools

import kivy
from kivy.uix.button import Button
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView 
from kivy.properties import ListProperty, StringProperty, NumericProperty, DictProperty
from kivy.uix.screenmanager import Screen
from kivy.config import Config
from kivy.graphics import *
from kivy.utils import get_color_from_hex

Config.set('graphics', 'width', '330')
Config.set('graphics', 'height', '652')
dst_dir = os.getcwd() + "\\book_covers\\"


class RootWidget(BoxLayout):
    pass


class HomeScreen(Screen):
    pass


class ShelfViewer(RecycleView): 
    def __init__(self, **kwargs): 
        super(ShelfViewer, self).__init__(**kwargs)
        self.data = SqliteDB.get_db_values('shelves')

    def add_shelf(self, shelf_title):
        if shelf_title:
            SqliteDB.insert_to('shelves', shelf_title)
            self.data.append({'shelf': shelf_title})
    
    def remove_shelf(self, shelf_title):
            SqliteDB.del_value_from('shelves', shelf_title, 'shelf')
            self.data.remove({'shelf': shelf_title})

# class DropDownShelfViewer(RecycleView): 
#     def __init__(self, **kwargs): 
#         super(DropDownShelfViewer, self).__init__(**kwargs)
#         self.data = SqliteDB.get_db_values('shelves')


class HomeButton(Button):
    line_color = ListProperty([1, 1, 1, 1], rebind=True)

    def set_underline(self, rgb_color):
        self.line_color = rgb_color


class AddScreen(Screen):
    title = StringProperty("")
    author = StringProperty("")
    category = StringProperty("")
    rating = NumericProperty(0)
    rented_person = StringProperty("")
    date_completed = StringProperty("")
    pages = NumericProperty(0)
    book_id = NumericProperty(0)
    description = StringProperty("")
    shelves = ListProperty()
    tags = ListProperty()

    def save_book(self, values):
        if self.book_id > 0:
            SqliteDB.edit_book_in_db(self.book_id, *values)
        else:
            SqliteDB.add_book_to_db(*values)

class BookItem(BoxLayout):
    title = StringProperty()
    cover = StringProperty()
    book_id = NumericProperty()
    shelves = StringProperty()



class FavButton(Button):
    is_fav = NumericProperty(0)
    
    def set_favourite(self, fav_input):
        if fav_input == 0:
            self.is_fav = 1
            self.children[0].source = 'images/heart_red.png'
        elif fav_input == 1:
            self.is_fav = 0
            self.children[0].source = 'images/heart.png'
    
    def load_favourite(self, fav_input):
        if fav_input == 1:
            self.is_fav = 1
            self.children[0].source = 'images/heart_red.png'
        elif fav_input == 0:
            self.is_fav = 0
            self.children[0].source = 'images/heart.png'


class AddImageButton(Button):
    imageDest = StringProperty('')
    
    def add_book_image(self, book_id):
        try:
            path = filechooser.open_file(title="Pick a book cover ...", 
                                         filters=[("*")])[0]
        except IndexError:
            return 0
        
        # TODO: save img as temp.jpg, then after book's save change it to id.jpg
        if book_id == 0:
            book_id = randint(9999, 999999)

        self.crop_and_resize(path, book_id)
        
        self.imageDest = dst_dir + str(book_id) + '.jpg'
        self.children[0].source = self.imageDest
    
    def load_book_image(self, path):
        if path:
            self.imageDest = path
        else:
            self.imageDest = 'images/cover_blank.png'
        
        self.children[0].source = self.imageDest
    
    def crop_and_resize(self, img_path, book_id):
        ratio = 475 / 300   # height / width
        size = (300, 475)

        original = Image.open(img_path)
        width, height = original.size   # Get dimensions 

        if width * ratio > height:
            new_width = height / ratio
            to_cut = width - new_width

            left = to_cut / 2
            top = 0
            right = width - (to_cut / 2)
            bottom = height

            cropped_img = original.crop((left, top, right, bottom))
        else:
            new_height = width * ratio
            to_cut = height - new_height

            left = 0
            top = to_cut / 2
            right = width
            bottom = height - (to_cut / 2)
            
            cropped_img = original.crop((left, top, right, bottom))

        cropped_img.thumbnail(size)

        cropped_img = cropped_img.convert('RGB')
        cropped_img.save(dst_dir + str(book_id) + '.jpg')


class ReadButton(Button):
    isRead = NumericProperty(0)

    def set_read_status(self, read_input):
        if read_input == 0:
            self.isRead = 1
            self.background_color = get_color_from_hex("#28527a")
            self.color = get_color_from_hex("#ffffff")

        elif read_input == 1:
            self.isRead = 0
            self.background_color = get_color_from_hex("#ffffff")
            self.color = get_color_from_hex("#28527a")

    def load_read_status(self, read_input):
        if read_input == 1:
            self.background_color = get_color_from_hex("#28527a")
            self.color = get_color_from_hex("#ffffff")
        elif read_input == 0:
            self.isRead = 0
            self.background_color = get_color_from_hex("#ffffff")
            self.color = get_color_from_hex("#28527a")


class StarsButton(BoxLayout):
    rating = NumericProperty()

    def set_rating(self, value):
        if value == 1:
            self.ids['first_s'].children[0].source = 'images/star_full.png'
            self.ids['sec_s'].children[0].source = 'images/star.png'
            self.ids['third_s'].children[0].source = 'images/star.png'
            self.ids['fourth_s'].children[0].source = 'images/star.png'
            self.rating = 1
        elif value == 2:
            self.ids['first_s'].children[0].source = 'images/star_full.png'
            self.ids['sec_s'].children[0].source = 'images/star_full.png'
            self.ids['third_s'].children[0].source = 'images/star.png'
            self.ids['fourth_s'].children[0].source = 'images/star.png'
            self.rating = 2
        elif value == 3:
            self.ids['first_s'].children[0].source = 'images/star_full.png'
            self.ids['sec_s'].children[0].source = 'images/star_full.png'
            self.ids['third_s'].children[0].source = 'images/star_full.png'
            self.ids['fourth_s'].children[0].source = 'images/star.png'
            self.rating = 3
        elif value == 4:
            self.ids['first_s'].children[0].source = 'images/star_full.png'
            self.ids['sec_s'].children[0].source = 'images/star_full.png'
            self.ids['third_s'].children[0].source = 'images/star_full.png'
            self.ids['fourth_s'].children[0].source = 'images/star_full.png'
            self.rating = 4


class ShelfItem(BoxLayout):
    shelf = StringProperty()
    # TODO:
    # book_count = NumericProperty(0)
    def open_shelf(self):
        for i in range(len(App.get_running_app().root.ids.rootmanager.screen_names)):
            if App.get_running_app().root.ids.rootmanager.screen_names[i].find('home') != -1:
                index = i

        App.get_running_app().root.ids['rootmanager'].screens[index].middlemanager.current = 'book'
        test = App.get_running_app().root.ids['rootmanager']
        
        App.get_running_app().root.ids['rootmanager'].screens[index].middlemanager.books_screen.book_scroll.search_shelf(self.shelf)

        print("AAAA")

class StatsScreen(Screen):
    top_authors = ListProperty()

    def __init__(self, **kwargs):
        super(StatsScreen, self).__init__(**kwargs)
        self.plot_data()
        self.top_authors = self.find_top_authors()
    
    def find_top_authors(self):
        books_data = SqliteDB.get_db_values('booktable')
        
        authors = defaultdict(int)
        for item in books_data:
            if item['isRead']:
                authors[item['author']] += 1

        top_authors = [(x, y) for x, y in itertools.islice(sorted(authors.items(), key=lambda item: item[1], reverse=True), 3)]

        if len(top_authors) < 3:
            top_authors.append(('', 0))
            top_authors.append(('', 0))
        
        return top_authors

    
    def plot_data(self):
        books_data = SqliteDB.get_db_values('booktable')

        " ----- Read books pie ----- "
        all_books = len(books_data)
        read_books = 0
        for item in books_data:
            if item['isRead']:
                read_books += 1

        counts = [all_books-read_books, read_books]
        explode = 2 * (0.025,)

        fig1, ax1 = plt.subplots()
        ax1.pie(counts, startangle=90, pctdistance=0.78, explode=explode)
        
        centre_circle = plt.Circle((0, 0), 0.65, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        
        textstr = f"Books read: {read_books}\n\n{read_books/all_books*100:0.0f}% of your library "
        
        plt.figtext(0.51, 0.45, textstr, fontsize=14)
        plt.subplots_adjust(right=0.5)

        plt.savefig("pie.png", bbox_inches='tight', pad_inches=0)

        " ----- Categories pie ----- "
        category_counts = defaultdict(int)
        for item in books_data:
            category_counts[item['category']] += 1
        
        categories = [ct if ct else 'no category' for ct in category_counts.keys()]

        def func(pct, allvals):
            absolute = int(pct/100.*sum(allvals))
            if pct < 3:
                return ""
            else:
                return "{:.0f}%\n({:d})".format(pct, absolute)
        
        fig1, ax1 = plt.subplots()
        explode = len(categories) * (0.05,)
        category_counts = list(category_counts.values())

        patches, texts, autotexts = ax1.pie(category_counts, autopct=lambda pct: func(pct, category_counts),
            startangle=90, pctdistance=0.8, explode=explode)

        ax1.legend(patches, categories,
                title="Categories            ",
                loc="center left",
                bbox_to_anchor=(0.95, 0, 0.5, 1),
                frameon=False,
                fontsize=12,
                title_fontsize=14)

        centre_circle = plt.Circle((0, 0), 0.65, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.subplots_adjust(right=0.5)

        plt.savefig("pie2.png", bbox_inches='tight', pad_inches=0)


class SmallShelfItem(BoxLayout):
    shelf = StringProperty()
    checkbox_img = StringProperty('images/checkbox_empty.png')       


class BookGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super(BookGridLayout, self).__init__(**kwargs)

        self.data = SqliteDB.get_db_values('booktable')

        for item in self.data:
            if not item['imageDest']:
                book_cover = 'images/cover_blank.png'
            else:
                book_cover = item['imageDest']

            book = BookItem(book_id=item['book_id'], title=item['title'], cover=book_cover, shelves=item['shelves'])
            self.add_widget(book)
            self.height += book.height / 3 + 10

    def search_title(self, title_str):
        books_to_del = []
        for book in self.children:
            test = book
            if title_str not in book.title:
                books_to_del.append(book)

        for b in books_to_del:
            self.remove_widget(b)

    def search_shelf(self, shelf_str):
        books_to_del = []
        for book in self.children:
            test = book
            if shelf_str not in book.shelves:
                books_to_del.append(book)

        for b in books_to_del:
            self.remove_widget(b)


class BookcaseApp(App):
    def build(self):
        self.title = 'BookByBook'
        # self.icon = ''

        SqliteDB()

        self.root = RootWidget()
        return self.root

    def format_book_title(self, book_title):
        book_title = book_title[:24]
        
        if book_title.count(' ') > 1:
            return book_title[:8] + book_title[8:].replace(' ', '\n', 1)
        else:
            return book_title.replace(' ', '\n', 1)

    def add_home_screen(self):
        index = 0
        for i in range(len(self.root.ids.rootmanager.screen_names)):
            if self.root.ids.rootmanager.screen_names[i].find('home') != -1:
                index = i
        
        self.root.ids['rootmanager'].remove_widget(self.root.ids.rootmanager.screens[index])
        self.root.ids['rootmanager'].add_widget(HomeScreen())

    def add_newbook_screen(self):
        index = 0
        for i in range(len(self.root.ids.rootmanager.screen_names)):
            if self.root.ids.rootmanager.screen_names[i].find('new') != -1:
                index = i
        
        self.root.ids['rootmanager'].remove_widget(self.root.ids.rootmanager.screens[index])
        self.root.ids['rootmanager'].add_widget(AddScreen())


    def open_edit_book(self, book_id):
        for i in range(len(self.root.ids.rootmanager.screen_names)):
            if self.root.ids.rootmanager.screen_names[i].find('new') != -1:
                index = i
        
        book_values = SqliteDB.get_single_book_from_db(book_id)
        self.root.ids['rootmanager'].remove_widget(self.root.ids.rootmanager.screens[index])
        self.root.ids['rootmanager'].add_widget(AddScreen(
            title = book_values['title'],
            author = book_values['author'],
            category = book_values['category'],
            rating = book_values['rating'],
            rented_person = book_values['rentedPerson'],
            date_completed = book_values['dateCompleted'],
            pages = book_values['pageCount'],
            book_id = book_id,
            description = book_values['describtion'],
            shelves = book_values['shelves'].split(';'),
            tags = book_values['tags'].split(';')
            ))

        self.root.ids['rootmanager'].current = 'new'
        self.root.ids['rootmanager'].screens[4].ids['stars_rating'].set_rating(book_values['rating'])
        self.root.ids['rootmanager'].screens[4].ids['fav_btn'].load_favourite(book_values['isFav'])
        self.root.ids['rootmanager'].screens[4].ids['read_btn'].load_read_status(book_values['isRead'])
        self.root.ids['rootmanager'].screens[4].ids['add_image_btn'].load_book_image(book_values['imageDest'])
        self.set_shelves_input()

    def set_shelves(self, shelf):
        if shelf not in self.root.ids['rootmanager'].screens[4].shelves:
            self.root.ids['rootmanager'].screens[4].shelves.append(shelf)
        else:
            self.root.ids['rootmanager'].screens[4].shelves.remove(shelf)
        
        self.set_shelves_input()


    def set_shelves_input(self):
        for i in range(len(self.root.ids.rootmanager.screen_names)):
            if self.root.ids.rootmanager.screen_names[i].find('new') != -1:
                index = i

        shelves = ';'.join(self.root.ids['rootmanager'].screens[index].shelves)
        shelves_data = self.root.ids['rootmanager'].screens[4].ids['shelf_input'].ids['drop_down_shelf_viewer'].data
        
        for shelf_dict in shelves_data:
            if shelf_dict['shelf'] in shelves:
                shelf_dict['checkbox_img'] = 'images/checkbox.png'
            else:
                shelf_dict['checkbox_img'] = 'images/checkbox_empty.png'

        # print(shelves_data)
        # print(self.root.ids['rootmanager'].screens[4].ids['shelf_input'].ids['drop_down_shelf_viewer'].data)






if __name__ == '__main__':
    BookcaseApp().run()
