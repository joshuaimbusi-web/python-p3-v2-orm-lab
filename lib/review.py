from __init__ import CURSOR, CONN 
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        # use the property setter so validation runs on construction
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        # enforce that year is an integer and not earlier than 2000
        if not isinstance(value, int):
            raise ValueError("year must be an int")
        if value < 2000:
            raise ValueError("year must be 2000 or later")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        # summary must be a non-empty string
        if not isinstance(value, str):
            raise ValueError("summary must be a string")
        if len(value.strip()) == 0:
            raise ValueError("summary cannot be empty")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # must be an int
        if not isinstance(value, int):
            raise ValueError("employee_id must be an int")
        # must refer to an existing Employee
        if Employee.find_by_id(value) is None:
            raise ValueError("employee_id must refer to an existing Employee")
        self._employee_id = value

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()
        cls.all.clear()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?);"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        self.__class__.all[self.id] = self
        return self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        if row is None:
            return None

        row_id, year, summary, employee_id = row

        # return cached instance if present (update its attributes)
        if row_id in cls.all:
            inst = cls.all[row_id]
            inst.year = year
            inst.summary = summary
            inst.employee_id = employee_id
            return inst

        # otherwise create new instance and cache it
        inst = cls(year, summary, employee_id, id=row_id)
        cls.all[row_id] = inst
        return inst
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        # check cache first
        if id in cls.all:
            return cls.all[id]

        CURSOR.execute("SELECT id, year, summary, employee_id FROM reviews WHERE id = ?;", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row)

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        if self.id is None:
            raise ValueError("Can't update a Review without an id. Save it first.")
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?;"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        # keep cache current
        self.__class__.all[self.id] = self
        return self

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        if self.id is None:
            return None
        CURSOR.execute("DELETE FROM reviews WHERE id = ?;", (self.id,))
        CONN.commit()
        if self.id in self.__class__.all:
            del self.__class__.all[self.id]
        self.id = None
        return None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        CURSOR.execute("SELECT id, year, summary, employee_id FROM reviews;")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
