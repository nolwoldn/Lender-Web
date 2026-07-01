from django.urls import path
from .views import (
    home,
    log_in,
    Search,
    api_search,
    log_out,
    sign_up,
    profile,
    report,
    check_user,
    borrow,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", log_in, name="login"),
    path("search/", Search, name="search"),
    path("api/search/", api_search),
    path("logout/", log_out, name="log_out"),
    path("signup/", sign_up, name="signup"),
    path("users/", check_user, name="profile-page"),
    path("profile/", profile, name="myacc"),
    path("report/", report, name="repo"),
    path("api/borrow/", borrow),
]
