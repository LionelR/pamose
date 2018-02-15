"""
Register Shell Contexts
"""
from pamose import models


def register(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': models.db,
            'User': models.User}

    app.shell_context_processor(shell_context)
