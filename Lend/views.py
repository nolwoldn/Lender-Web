from django.shortcuts import redirect, render
import json
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Item, Users, Error_reporting, Borrow_request
import base64
from django.core.files.base import ContentFile
import os
import random
from django.views.decorators.csrf import csrf_protect


# Create your views here.
@csrf_protect
def find_I_tBQ(b_ID):
    brr_req = Borrow_request.objects.filter(id=b_ID).first()
    item = Item.objects.filter(id=brr_req.Borrowing_item_id).first()

    return [item, brr_req]


def find_BQ_tI(i_ID):
    brr_req = Borrow_request.objects.filter(Borrowing_item_id=i_ID)

    return brr_req


def authenticate(username, password):
    user = Users.objects.filter(Name=username).first()
    if user is not None:
        if user.Password == password:
            return user
        else:
            return None
    else:
        return None


def log_in(request):
    context = {"Login_fail": False}
    if request.session.get("usr_session"):
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("Name")
        password = request.POST.get("password")
        remember = request.POST.get("Remember")

        user = authenticate(username, password)
        if user is not None:
            request.session["usr_session"] = user.id

            if remember:
                request.session.set_expiry(2592000)
            else:
                request.session.set_expiry(0)

            return redirect("home")

        else:
            context["Login_fail"] = True
            pass

    return render(request, "Login.html", context)


def find_item(user_id):
    lender = Users.objects.filter(id=user_id).first()
    items = Item.objects.filter(id__in=lender.Lended_items_id)

    combined = [
        {
            "lender": {"name": lender.Name, "link": lender.id},
            "item": {
                "name": i.Item_name,
                "desc": i.Item_desc,
                "borrowed": i.Item_borrowed_state,
                "url": i.Item_image.url if i.Item_image else None,
                "id": i.id,
                "brrw_req_id": find_BQ_tI(i.id),
            },
        }
        for i in items
    ]

    return combined[0] if len(combined) == 1 else combined


def log_out(request):
    if "usr_session" in request.session:
        del request.session["usr_session"]
    return redirect("login")


def home(request):
    user_session = request.session.get("usr_session")

    if not user_session:
        return redirect("login")

    current_user = Users.objects.filter(id=user_session).first()
    if not current_user:
        return redirect("login")

    users = Users.objects.all().values()

    items = []

    for i in users:
        data = find_item(i["id"])

        if type(data) is list:
            for x in data:
                x["item"]["desc"] = x["item"]["desc"][0:14] + "..."
                x["item"]["name"] = x["item"]["name"][0:10] + "..."
                if x["lender"]["link"] == request.session["usr_session"]:
                    continue

                items.append(x)
        else:
            if data["lender"]["link"] == request.session["usr_session"]:
                continue
            items.append(data)

    if len(items) == 0:
        items = [False]

    context = {
        "username": current_user.Name[0:15],
        "person_link": current_user.id,
        "items": items,
    }

    return render(request, "Home.html", context)


def find_through_search(query):

    full_comp_ls = []

    items = Item.objects.filter(
        Q(Item_desc__icontains=query) | Q(Item_name__icontains=query)
    ).exclude(Item_borrowed_state=True)

    for i, x in enumerate(items):
        lender = Users.objects.filter(Lended_items_id__contains=x.id).first()

        adding_dict = {
            "lender": {
                "name": lender.Name,
                "link": lender.id,
            },
            "items": {"name": x.Item_name, "desc": x.Item_desc, "id": x.id},
        }
        full_comp_ls.append(adding_dict)

    return full_comp_ls


def Search(request):
    query = request.GET.get("q", "").strip()

    context = {
        "items_found": (find_through_search(query)),
        "query": query.strip(),
    }
    return render(request, "Search_page.html", context)


def api_search(request):
    query = request.GET.get("q", "").strip()
    if request.session.get("usr_session") is None:
        return redirect("login")

    if query == "":
        return redirect("home")

    item = find_through_search(query)

    return JsonResponse({"item": item})


def sign_up(request):
    context = {"user_found": False}
    user_session = request.session.get("usr_session")

    if user_session:
        return redirect("home")
    if request.method == "POST":
        name = request.POST.get("name")

        if len(name) > 30:
            name = name[0:30]

        password = request.POST.get("password")
        if len(password) > 30:
            password = password[0:30]

        users = Users.objects.filter(Name=name)

        if users.exists():
            context["user_found"] = True
            return render(request, "sign_up.html", context)

        user = Users(Name=name, Password=password)
        user.save()
        return redirect("login")

    return render(request, "sign_up.html", context)


def query_check(query):
    valid_query = True

    try:
        query = int(query)
    except Exception:
        valid_query = False

    if type(query) is not int:
        valid_query = False

    return valid_query


def check_user(request):
    query = request.GET.get("q", "").strip()
    usr_session = request.session["usr_session"]

    if int(usr_session) == int(query):
        return redirect("myacc")

    if usr_session is None:
        return redirect("Login")

    if not query_check(query):
        return HttpResponse("<h1>Fail</h1>")

    crr_usr = Users.objects.filter(id=usr_session).first()
    queryed_usr = Users.objects.filter(id=query)

    if not queryed_usr.exists():
        return render(request, "UserNotFound.html", {"username": crr_usr.Name})
    found_usr = queryed_usr.first()
    itms = find_item(found_usr.id)
    itms_exist = True
    if type(itms) is dict:
        itms = [itms]
    if len(itms) == 0:
        itms_exist = False

    context = {
        "username": crr_usr.Name,
        "itms": itms,
        "itms_exist": itms_exist,
        "queryed_username": found_usr.Name,
    }

    return render(request, "viewUser.html", context)


class Profile_actions:
    def __init__(self, user, data=None):
        self.user = user
        self.data = data

    def decode_image(self, img, item_name):
        if img:
            format, imgStr = img.split(";base64,")
            extension = format.split("/")[-1]
            file_name = (
                f"{item_name}__{random.random() + random.randint(0, 1000)}.{extension}"
            )
            img_dir = os.path.join(
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "media",
                ),
                "item_images",
            )
            img_dir_ls = os.listdir(img_dir)

            while file_name in img_dir_ls:
                file_name = (
                    f"{item_name}__{random.random() + random.randint(0, 100000)}"
                )
            file_dat = ContentFile(base64.b64decode(imgStr), file_name)
            return file_dat
        return None

    def lend_item(self):
        item_name = self.data["itemName"].strip()
        item_desc = self.data["itemDesc"].strip()
        item_image_str = self.data["itemImage"]  # the base 64 text verison of the image

        new_item = Item(
            Item_name=item_name, Item_desc=item_desc, Item_borrowed_state=False
        )

        new_item.Item_image = self.decode_image(img=item_image_str, item_name=item_name)

        if len(item_name) > 32:
            item_name = item_name[0:32]

        if len(item_desc) > 1144:
            item_desc = item_desc[0:1144]

        usr_lended_itms_id = self.user.Lended_items_id

        new_item.save()
        usr_lended_itms_id.append(new_item.id)
        self.user.Lended_items_id = usr_lended_itms_id
        self.user.save()

    def return_item(self):
        itm = Item.objects.filter(id=self.data).first()

        user_borrowed_ls = self.user.Borrowed_items_id
        if itm.id not in user_borrowed_ls:
            return

        user_borrowed_ls.remove(itm.id)
        self.user.Borrowed_items_id = user_borrowed_ls  # user modified remeber to save
        itm.Item_borrowed_state = False  # itm modified remeber to save

        itm.save()
        self.user.save()

    def change_brrw_req(self):
        borrowr_req = Borrow_request.objects.filter(id=self.data["borrowId"]).first()
        itm = Item.objects.filter(id=borrowr_req.Borrowing_item_id).first()
        borrwing_usr = Users.objects.filter(id=borrowr_req.Borrowing_user_id).first()
        acceptance = self.data["isAccepted"]
        user_ls = self.user.Lended_items_id

        if itm.id not in user_ls:
            return

        if itm.Item_borrowed_state:
            return

        if acceptance:
            itm.Item_borrowed_state = True  # modal update
            borrwing_U_L = set(borrwing_usr.Borrowed_items_id)

            borrwing_U_L.add(itm.id)
            borrwing_usr.Borrowed_items_id = list(borrwing_U_L)  # modal update

            itm.save()
            borrwing_usr.save()
            borrowr_req.delete()

        else:
            itm.Item_borrowed_state = False  # modal update
            itm.save()
            borrowr_req.delete()

    def edit_itm(self):
        itm = Item.objects.filter(id=self.data["itm_Id"]).first()
        item_img = self.data["itm_new_img"]
        user_ls = self.user.Lended_items_id
        if itm.id not in user_ls:
            return

        itm.Item_name = self.data["itm_new_name"]
        itm.Item_desc = self.data["itm_new_desc"]
        if itm.Item_image and os.path.exists(itm.Item_image.path) and item_img is not None:
            os.remove(itm.Item_image.path)
            itm.Item_image = self.decode_image(
                img=item_img, item_name=self.data["itm_new_name"]
            )

        itm.save()

    def delete_itm(self):
        user_ls = self.user.Lended_items_id
        itm = Item.objects.filter(id=self.data).first()

        if itm.id not in user_ls:
            return

        borrow_reqs = Borrow_request.objects.filter(Borrowing_item_id=itm.id)
        for borrw_req in borrow_reqs:
            borrw_req.delete()  # modal change
        user_ls.remove(itm.id)
        self.user.Lended_items_id = user_ls  # modal update
        borrowing_usr = Users.objects.filter(Borrowed_items_id__contains=itm.id)
        if borrowing_usr.exists():
            borrowing_usr_ls = borrowing_usr.Borrowed_items_id
            for i in borrowing_usr_ls:
                y = i.Borrowed_items_id
                y.remove(itm.id)
                i.Borrowed_items_id = y  # modal update
                i.save()

        if itm.Item_image and os.path.exists(itm.Item_image.path):
            os.remove(itm.Item_image.path)

        itm.delete()
        self.user.save()


def profile(request):
    user_sess = request.session.get("usr_session")
    user = Users.objects.filter(id=user_sess).first()

    if user_sess is None:
        return redirect("login")

    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            action = payload.get("action")
            data = payload.get("data")
            prof = Profile_actions(user=user, data=data)
            match action:
                case "lendingItem":
                    prof.lend_item()
                    return JsonResponse({"worked": True})

                case "returnItem":
                    prof.return_item()
                    return JsonResponse({"worked": True})
                case "affectBorrowReq":
                    prof.change_brrw_req()
                    return JsonResponse({"worked": True})
                case "editItm":
                    prof.edit_itm()
                    return JsonResponse({"worked": True})
                case "delete_itm":
                    prof.delete_itm()
                    return JsonResponse({"worked": True})

                case _:
                    return redirect("login")
        except Exception as e:
            print(f"{e}")
            return JsonResponse({"worked": False, "error": e})

    borrow_requests = Borrow_request.objects.filter(user_Borrowing_from_id=user.id)

    borrow_req = []
    user_items = find_item(user.id)

    if type(user_items) is dict:
        user_items = [user_items]

    for i in borrow_requests:
        if len(borrow_requests) == 0:
            borrow_req.append(
                {"usr_id": "None", "Name": "None Found", "Item": "None Found"}
            )
            break

        borrowing_user = Users.objects.filter(id=i.Borrowing_user_id).first()
        borrowing_item = Item.objects.filter(id=i.Borrowing_item_id).first()
        full_dict = {
            "usr_id": borrowing_user.id,
            "Name": borrowing_user.Name,
            "Item": borrowing_item.Item_name,
            "brrw_req_id": i.id,
        }

        borrow_req.append(full_dict)

    items = [
        {
            "Name": i["item"]["name"],
            "desc": i["item"]["desc"],
            "borrowed": i["item"]["borrowed"],
            "id": i["item"]["id"],
            "borrow_req_id": i["item"]["brrw_req_id"],
            "image": i["item"]["url"],
        }
        for i in user_items
    ]
    usr_borrowed_itms = []

    for b_ID in user.Borrowed_items_id:
        b_I_ = Item.objects.filter(id=b_ID).first()
        i_O_U = Users.objects.filter(Lended_items_id__contains=b_I_.id).first()

        usr_borrowed_itms.append(
            {
                "Item_name": b_I_.Item_name,
                "Item_id": b_ID,
                "User_name": i_O_U.Name,
                "brrwd": True,
            }
        )
    if len(user.Borrowed_items_id) == 0:
        usr_borrowed_itms = [{"brrwd": False}]

    context = {
        "username": user.Name,
        "borrow_req": borrow_req,
        "No_items": False,
        "user_items": items,
        "brrd_itms": usr_borrowed_itms,
        "borrow_req_len": len(borrow_req),
        "fall-back-image": os.path.join(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "item_images",
            ),
            "Untitled.jpg",
        ),
    }

    if len(items) == 0:
        context["No_items"] = True

    return render(request=request, template_name="profile.html", context=context)


def report(request):

    user_session = request.session.get("usr_session")

    if not user_session:
        return redirect("login")

    curr_user = Users.objects.filter(id=user_session).first()
    context = {
        "username": curr_user.Name,
        "person_link": curr_user.id,
        "reported": False,
    }
    if request.method == "POST":
        text = request.POST.get("report-text").strip()
        if len(text) > 255:
            text = text[0:255]
        usr_id = curr_user.id

        checking_report = Error_reporting.objects.filter(report=text)
        if checking_report.exists():
            context["reported"] = True
            return render(request, "Reporting_page.html", context)

        report = Error_reporting(reporting_usr=usr_id, report=text)
        report.save()

        context["reported"] = True

    return render(request, "Reporting_page.html", context)


def borrow(request):

    if not request.method == "POST":
        return redirect("login")

    crr_usr = request.session.get("usr_session")
    payload = json.loads(request.body)
    borrwing_from_usr_id = payload.get("borrowing_from_id")
    borrowing_itm_id = payload.get("borrowing_itm_id")

    other_brrw_req = Borrow_request.objects.filter(
        Borrowing_user_id=crr_usr,
        user_Borrowing_from_id=borrwing_from_usr_id,
        Borrowing_item_id=borrowing_itm_id,
    )
    if other_brrw_req.exists():
        what_happened = "You have already sent the request."

        return JsonResponse({"what": what_happened})

    what_happened = "nothing"

    item_test = Item.objects.filter(id=borrowing_itm_id).first()

    brrw_req = Borrow_request(
        Borrowing_user_id=crr_usr,
        user_Borrowing_from_id=borrwing_from_usr_id,
        Borrowing_item_id=borrowing_itm_id,
    )

    brrw_req.save()

    if item_test.Item_borrowed_state:
        brrw_req.delete()
        what_happened = "Item borrowed"
        return JsonResponse({"what": what_happened})

    return JsonResponse({"what": what_happened})


def account_deletion(request):
    if not request.session.get("usr_session"):
        return redirect("home")

    if not request.method == "POST":
        return render(request, "deleteAccountPage.html")

    usr_session = request.session["usr_session"]

    usr_acc = Users.objects.filter(id=usr_session)

    if not usr_acc.exists():
        return redirect("home")

    usr_acc = usr_acc.first()

    usr_id = usr_acc.id
    usr_itms = Item.objects.filter(id__in=usr_acc.Lended_items_id)
    usr_borrow_req = Borrow_request.objects.filter(Borrowing_user_id=usr_id)
    usr_borrowed_itms = Item.objects.filter(id__in=usr_acc.Borrowed_items_id)
    usr_final_repo = request.POST.get("fin-repo")[0:1200].strip()
    usr_error_repos = Error_reporting.objects.filter(reporting_usr=usr_id)

    if usr_itms.exists():
        for i in usr_itms:
            if i.Item_image and os.path.exists(i.Item_image.path):
                os.remove(i.Item_image.path)
            i.delete()
    if usr_borrow_req.exists():
        for i in usr_borrow_req:
            i.delete()
    if usr_error_repos.exists():
        if len(usr_final_repo) > 0:
            final_repo = Error_reporting(reporting_usr=0, report=usr_final_repo)
        for i in usr_error_repos:
            i.reporting_usr = 0
            i.save(force_update=True)
        final_repo.save()

    for i in usr_borrowed_itms:
        i.Item_borrowed_state = False
        i.save()

    if len(usr_acc.Borrowed_items_id) > 0:
        for i in usr_acc.Borrowed_items_id:
            crr_prof = Profile_actions(user=usr_acc, data=i)
            crr_prof.return_item()

    usr_acc.delete()
    log_out(request)

    return redirect("signup")
