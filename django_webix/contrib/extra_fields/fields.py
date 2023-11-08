class NotDbColumnField:
    db_collation = False

    def get_attname_column(self):
        attname = self.get_attname()
        return attname, None  # None for concrete=False -> not caming from DB
