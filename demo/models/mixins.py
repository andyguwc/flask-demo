# -*- coding: utf-8 -*-
from datetime import datetime
from demo.extensions import db


class ResourceMixin(object):
    # Keep track when records are created and updated.
    created_on = db.Column(db.DateTime(),
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    updated_on = db.Column(db.DateTime(),
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def save(self):
        """
        Save a model instance.
        """
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        """
        Delete a model instance.
        """
        db.session.delete(self)
        return db.session.commit()

    def __str__(self):
        """
        Create a human readable version of a class instance.
        """
        obj_id = hex(id(self))
        columns = self.__table__.c.keys()

        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in columns)
        return '<%s %s(%s)>' % (obj_id, self.__class__.__name__, values)
