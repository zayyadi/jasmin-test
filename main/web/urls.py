from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("filters/manage/", views.filters_view_manage, name="filters_view_manage"),
    path("filters/", views.filters_view, name="filters_view"),
    path("groups/manage/", views.groups_view_manage, name="groups_view_manage"),
    path("groups/", views.groups_view, name="groups_view"),
    path("httpccm/manage/", views.httpccm_view_manage, name="httpccm_view_manage"),
    path("httpccm/", views.httpccm_view, name="httpccm_view"),
    path("morouter/manage/", views.morouter_view_manage, name="morouter_view_manage"),
    path("morouter/", views.morouter_view, name="morouter_view"),
    path("mointerceptor/", views.mointerceptor_view, name="mointerceptor_view"),
    path(
        "mointerceptor/manage/",
        views.mointerceptor_view_manage,
        name="mointerceptor_view_manage",
    ),
    path(
        "mtinterceptor/", views.mtinterceptor_view, name="mtinterceptor_view"
    ),  # noqa: F405
    path(
        "mtinterceptor/manage/",
        views.mtinterceptor_view_manage,
        name="mtinterceptor_view_manage",
    ),
    path("mtrouter/manage/", views.mtrouter_view_manage, name="mtrouter_view_manage"),
    path("mtrouter/", views.mtrouter_view, name="mtrouter_view"),
    path("smppccm/manage/", views.smppccm_view_manage, name="smppccm_view_manage"),
    path("smppccm/", views.smppccm_view, name="smppccm_view"),
    path("smppccm/monitor", views.smppc_monitor, name="smppc_monitor"),
    path(
        "submit_logs/manage/",
        views.submit_logs_view_manage,
        name="submit_logs_view_manage",
    ),
    path("submit_logs/", views.submit_logs_view, name="submit_logs_view"),  # noqa: F405
    path("users/manage/", views.users_view_manage, name="users_view_manage"),
    path("users/", views.users_view, name="users_view"),
    path("manage/", views.global_manage, name="global_manage"),
    path("", views.dashboard_view, name="dashboard_view"),
    path(
        "stats/",
        views.stats_view,
        name="stats_view",
    ),
    path(
        "stats/send_email_notification/<str:cid>",
        views.send_email_notification,
        name="send_email_notification",
    ),
    path(
        "stats/manage/",
        views.stat_view_manage,
        name="stats_view_manage",
    ),
    path(
        "http_stats/",
        views.http_stats_view,
        name="http_stats_view",
    ),
    path(
        "http_stats/manage/",
        views.http_stat_view_manage,
        name="http_stats_view_manage",
    ),
    path(
        "smpp_stats/",
        views.smpp_stats_view,
        name="smpp_stats_view",
    ),
    path(
        "smpp_stats/manage/",
        views.smpp_stat_view_manage,
        name="smpp_stats_view_manage",
    ),
    path(
        "users_stats/",
        views.user_stats_view,
        name="user_stats_view",
    ),
    path(
        "users_stats/manage/",
        views.user_stat_view_manage,
        name="user_stats_view_manage",
    ),
    path(
        "user_stats/send_email_notification/<str:uid>",
        views.user_email_notification,
        name="user_email_notification",
    ),
    path(
        "settings/",
        views.settings,
        name="setting",
    ),
    path(
        "settings/monitor/",
        views.monitor_settings,
        name="settings",
    ),
    path(
        "settings/monitor/manage/",
        views.settings_manage,
        name="settings_manage",
    ),
    path(
        "user_settings/",
        views.user_settings,
        name="user_settings",
    ),
    path(
        "user_settings/manage/",
        views.user_manage,
        name="user_manage",
    ),
]
