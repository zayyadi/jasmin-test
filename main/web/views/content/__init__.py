from .filters import filters_view, filters_view_manage  # noqa: F401
from .groups import groups_view, groups_view_manage  # noqa: F401
from .httpccm import httpccm_view, httpccm_view_manage  # noqa: F401
from .morouter import morouter_view, morouter_view_manage  # noqa: F401
from .mtrouter import mtrouter_view, mtrouter_view_manage  # noqa: F401
from .smppccm import (
    smppccm_view,  # noqa: F401
    smppccm_view_manage,  # noqa: F401
    smppc_monitor,  # noqa: F401
    # noqa: F401
)
from .submit_logs import submit_logs_view, submit_logs_view_manage  # noqa: F401
from .users import users_view, users_view_manage  # noqa: F401
from .mointerceptor import mointerceptor_view, mointerceptor_view_manage  # noqa: F401
from .mtinterceptor import mtinterceptor_view, mtinterceptor_view_manage  # noqa: F401
from .stats import stat_view_manage, stats_view, send_email_notification  # noqa: F401
from .user_stats import (
    user_stats_view,  # noqa: F401
    user_stat_view_manage,  # noqa: F401
    user_email_notification,  # noqa: F401
)  # noqa: F401
from .smpp_server_stat import smpp_stat_view_manage, smpp_stats_view  # noqa: F401
from .http_server_stat import http_stats_view, http_stat_view_manage  # noqa: F401
from .setting import (
    settings,  # noqa: F401
    monitor_settings,  # noqa: F401
    settings_manage,  # noqa: F401
    # noqa: F401
    # SettingsDeleteView,  # noqa: F401
)
from .user_settings import user_settings, user_manage  # noqa: F401
