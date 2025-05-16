from .StaffRoutes import StaffRoutes # noqa: F401
from .BookingRoutes import BookingRoutes  # noqa: F401
from .InfoRoutes import InfoRoutes # noqa: F401
from .UserRoutes import UserRoutes # noqa: F401
from .DetailRoutes import DetailRoutes # noqa: F401
from .PaymentRoutes import PaymentRoutes # noqa: F401
from .AdminRoutes import AdminRoutes # noqa: F401
from .EventRoutes import EventRoutes # noqa: F401

__all__ = ['StaffRoutes', 'AdminRoutes', 'BookingRoutes', 'InfoRoutes', 'UserRoutes', 'DetailRoutes', 'PaymentRoutes', 'EventRoutes']