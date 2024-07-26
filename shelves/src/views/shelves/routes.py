from flask import render_template, request, Blueprint, redirect, flash
from flask_login import login_required, current_user
from os import path

from src.config import Config
from src.ext import db
from src.views.shelves.form import ShelfForm, BookForm
from src.models import Books, Shelf, User

TEMPLATE_FOLDER = path.join(Config.PROJECT_ROOT, "templates")
shelves_bp = Blueprint("shelves", __name__, template_folder=TEMPLATE_FOLDER)



# -------------
# ---SHELVES---
# -------------

# profile page, where shelves are shown
@shelves_bp.route("/shelves", methods=['GET', 'POST'])
@login_required
def shelves():
    shelves = Shelf.query.filter_by(user_id=current_user.id).all()
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("shelves.html", shelves=shelves, user=user)


# add shelf
@shelves_bp.route("/shelves/add_shelf", methods=["GET", "POST"])
@login_required
def add_shelf():
    
    form = ShelfForm()  
    if form.validate_on_submit():
        new_shelf = Shelf(shelf_name=form.shelf_name.data, user_id=current_user.id)
        db.session.add(new_shelf)
        db.session.commit()
        flash("Shelf added successfully!")
        print(f"Added new shelf: {new_shelf.shelf_name}")
        return redirect("/shelves/add_shelf")
    else:
        print("Form validation failed or not submitted yet.")
        print(form.errors)
    
    return render_template("add_shelf.html", form=form)


# delete shelf
@shelves_bp.route("/shelves/delete_shelf/<int:id>")
@login_required
def delete_shelf(id):
    shelf = Shelf.query.get(id)
    db.session.delete(shelf)
    db.session.commit()
    
    flash("Removed shelf")
    return redirect("/shelves")
    
    
# edit shelf
@shelves_bp.route("/shelves/edit_shelf/<int:id>", methods=["GET", "POST"])
@login_required
def edit_shelf(id):
    shelf = Shelf.query.get(id)
    if not shelf:
        flash("Shelf not found")
        return redirect("/shelves")
    
    form = ShelfForm(obj=shelf)
    if form.validate_on_submit():
        shelf.shelf_name = form.shelf_name.data
        
    db.session.commit()
    
    return render_template("add_shelf.html", form=form)


# -----------
# ---BOOKS---
# -----------

# show books of a selected shelf
@shelves_bp.route("/shelves/<int:id>", methods=['GET', 'POST'])
@login_required
def books(id):
    user = User.query.filter_by(id=current_user.id).first()
    shelves = Shelf.query.filter(Shelf.id!=id).all()
    
    if request.method == 'POST':
        search_query = request.form['query']
        chosen_books_list = Books.query.filter(
            ((Books.title.ilike(f'%{search_query}%')) | (Books.author.ilike(f'%{search_query}%'))) & (Books.user_id==current_user.id) & (Books.borrowed==False)
        ).all()
        borroweds_list = Books.query.filter(
            ((Books.title.ilike(f'%{search_query}%')) | (Books.author.ilike(f'%{search_query}%'))) & (Books.user_id==current_user.id) & (Books.borrowed==True)
        ).all()
    else:
        books = Books.query.filter_by(shelf_id=id)
        
        chosen_books = books.filter_by(borrowed=False).all()
        chosen_books_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'shelf_id' : book.shelf_id} for book in chosen_books]
    
        borroweds = books.filter_by(borrowed=True).all()
        borroweds_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'shelf_id' : book.shelf_id} for book in borroweds]
    return render_template("books.html", books=chosen_books_list, shelf_id=id, user=user, borroweds=borroweds_list, shelves=shelves)


# add book
@shelves_bp.route("/shelves/<int:shelf_id>/add_book", methods=["GET", "POST"])
@login_required
def add_book(shelf_id):
    form = BookForm()  
    if form.validate_on_submit():
        new_book = Books(title=form.title.data, author=form.author.data, shelf_id=shelf_id, user_id=current_user.id)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully!")
        return redirect(f"/shelves/{shelf_id}/add_book")
    else:
        print("Form validation failed or not submitted yet.")
        print(form.errors)
    
    return render_template("add_book.html", form=form, id=shelf_id)


# delete book
@shelves_bp.route("/shelves/<int:shelf_id>/delete_book/<int:book_id>")
@login_required
def delete_book(shelf_id, book_id):
    book = Books.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    
    flash("Removed book")
    return redirect(f"/shelves/{shelf_id}")


# borrow book
@shelves_bp.route("/shelves/<int:shelf_id>/borrow_book/<int:book_id>")
@login_required
def borrow_book(shelf_id, book_id):
    book = Books.query.filter_by(id=book_id).first_or_404()
    if book:
        book.borrowed = True
        db.session.commit()
    return redirect(f"/shelves/{shelf_id}")


# put back the borrowed book
@shelves_bp.route("/shelves/<int:shelf_id>/put_back_book/<int:book_id>")
@login_required
def put_back_book(shelf_id, book_id):
    book = Books.query.filter_by(id=book_id).first_or_404()
    if book:
        book.borrowed = False
        db.session.commit()
    return redirect(f"/shelves/{shelf_id}")


# move book
@shelves_bp.route("/shelves/move_book", methods=['POST'])
@login_required
def move_book():
    option=request.form.get('shelect')
    print(option)
    return redirect("/shelves")
    


# search books
@shelves_bp.route("/shelves/search", methods=['GET', 'POST'])
@login_required
def search():
    user = User.query.filter_by(id=current_user.id).first()
    results = []
    if request.method == 'POST':
        search_query = request.form['query']
        results = Books.query.filter(
            ((Books.title.ilike(f'%{search_query}%')) | (Books.author.ilike(f'%{search_query}%'))) & (Books.user_id==current_user.id)
        ).all()
    return render_template("search.html", results=results, user=user)