# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.repository import Repository  # noqa
from app.models.pull_request import PullRequest  # noqa
from app.models.review_job import ReviewJob  # noqa
from app.models.review_result import ReviewResult  # noqa
