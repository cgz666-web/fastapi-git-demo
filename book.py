from fastapi import APIRouter

book1 = APIRouter()

@book1.get('/')
def index():
    return {'message': 'book'}