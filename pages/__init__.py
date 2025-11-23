from flask import Blueprint
from .login import login_bp
from .logout import logout_bp
from .add import add_bp
from .action import action_bp
from .root import root_bp

blueprint = Blueprint("main", __name__)
blueprint.register_blueprint(login_bp)
blueprint.register_blueprint(logout_bp)
blueprint.register_blueprint(add_bp)
blueprint.register_blueprint(action_bp)
blueprint.register_blueprint(root_bp)
