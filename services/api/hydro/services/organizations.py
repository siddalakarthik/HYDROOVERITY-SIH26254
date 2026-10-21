"""OrganizationService persistent operations."""

from ..db import one
from .base import Service


class OrganizationService(Service):
    def run(self, b, parent=None):
        s, c = self.s, self.c
        return s.view("organizations", one(c, "SELECT * FROM organizations WHERE id=:o", o=self.o))
