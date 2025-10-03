class NotDbColumnField:
    db_collation = False

    # skip Model.full_clean validation, the field is present in _meta.fields but
    # is not present in the object instance.
    generated = True

    def get_attname_column(self):
        attname = self.get_attname()
        return attname, None  # None for concrete=False -> not caming from DB
