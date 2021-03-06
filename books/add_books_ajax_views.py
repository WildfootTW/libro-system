# The purpose of this file is to checking ISBN and return results to user browser when they keyin ISBN
# 2. receive book detail to store them
from django.http import JsonResponse
import sys, os
GET_BOOK_DETAIL = os.path.join(os.path.dirname(__file__), "get_books_detail")
sys.path.append(GET_BOOK_DETAIL)
from get_book_detail import get_book_detail
from books import sql_operation
from books import utils

def response_receive_ajax(request):
    return JsonResponse(request.POST, safe=False)

def isbn_to_detail(request):
    if request.is_ajax():
        isbn_input = request.POST["isbn_input"]

        response_object = {}

        try:
            check = sql_operation.check()
            check.check_identifier_valid(str(isbn_input))
        except utils.IndustryIdentifierError as error_paramenter:
            response_object["status"] = "invalid_identifier"
        else:
            response_object = get_book_detail(isbn_input)
            response_object["status"] = "success"

        return JsonResponse(response_object, safe=False)

def detail_to_store(request):
    if request.is_ajax():
        book_detail = {}
        book_detail["title"] = request.POST["detail_title"]
        book_detail["subtitle"] = request.POST["detail_subtitle"]
        book_detail["publisher"] = request.POST["detail_publisher"]
        book_detail["publisheddate"] = request.POST["detail_publisheddate"]
        book_detail["description"] = request.POST["detail_description"]
        book_detail["pk"] = request.POST["detail_pk"]
        book_detail["authors"] = request.POST.getlist("detail_authors[]")

        identifiers_not_split = request.POST.getlist("detail_identifiers[]")
        identifiers_splited = []
        for identifier in identifiers_not_split:
            identifiers_splited.append({
                "type" : identifier.split(":")[0],
                "identifier" : identifier.split(":")[1]
                })
        book_detail["identifiers"] = identifiers_splited

        #return JsonResponse(book_detail, safe=False)

        substance_information = {}
        substance_information["location"] = request.POST["information_location"]
        substance_information["possessor"] = request.POST["information_possessor"]
        substance_information["notas"] = request.POST["information_notas"]

        response_object = {}
        try:
            check = sql_operation.check()
            check.check_identifiers_valid(book_detail)
            check.check_title_not_empty(book_detail)
            check.check_duplicate_books(book_detail)
        except utils.IndustryIdentifierError as error_paramenter:
            response_object["status"] = "invalid_identifier"
            response_object["invalid_identifier"] = error_paramenter.error_identifier
        except utils.BookdetailValidError as error_paramenter:
            response_object["status"] = error_paramenter.message
        except utils.IndustryIdentifierDuplicate as error_paramenter:
            response_object["status"] = error_paramenter.message
#            response_object["duplicate_identifier"] = error_paramenter.duplicate_identifier
#            response_object["database_book"] = utils.bookdetail_2_dictionary(error_paramenter.duplicate_book)
            response_object["user_book"] = book_detail
            response_object["pk"] = error_paramenter.duplicate_book.pk
        except:
            response_object["status"] = "Unexpected Error"
            raise
        else:
            response_object["status"] = "success"

        if response_object["status"] == "success":
            store = sql_operation.store()
            #store.store_book_detail(book_detail)
            store.store_book(book_detail, substance_information)
        
        return JsonResponse(response_object, safe=False)
