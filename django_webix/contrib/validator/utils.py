
import inspect
from collections import OrderedDict

import magic
import numpy as np
import os
import pandas as pd
import geopandas
import tempfile
import zipfile
import io
from django.contrib.gis import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _
from xlrd import colname as xlcolname

from django_webix.contrib.validator.models import ImportFile

MIME = {
    'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/xml'],
    'xls': ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel',
            'application/x-ms-excel', 'application/x-excel', 'application/x-dos_ms_excel',
            'application/xls', 'application/x-xls', 'application/vnd.ms-office',
            'application/vnd-xls', 'application/excel'],
    'csv': ['text/csv', 'text/x-csv', 'application/csv', 'application/x-csv',
            'text/csv', 'text/comma-separated-values', 'text/x-comma-separated-values'],
    'txt': ['text/plain', 'text/tab-separated-values'],
    'zip': ['application/zip', 'text/plain']
}

ERR_MSG = {
    'NOFILE': _('No file uploaded'),
    'PARSE_ERR': _('Text file not recognizable as delimiter-separated values with separator \' {} \' (Exception:{})'),
    'WRONG_FILE': _('Could not find file \'{}\' (or read from buffer)'),
    'WRONG_EXT': _('File format \'{}\' not recognized, supported formats: {}'),
    'WRONG_TYPE': _('File type \'{}\' not supported'),
    'NOFOGLI': _('There is no sheet'),
    'NODATA': _('There is no data in the sheet {}'),
    'UNAMED_COLS': _('There are columns with no name'),
    'UNAMED_COLS_XL': _('There are columns with no name: {}'),
    'LESS_COLS': _('There are not enough columns: there are {} columns, {} needed'),
    'HEADER': _('Column headers ({}^ row) are incorrect'),
    'COLUMN': _('There is no column \'{}\''),
    'COL_POS': _('The name of the {}^ column ({}) must be \' {} \' (instead of \'{}\')'),
    'UNIQ_VIOLATION': _('A uniqueness rule has been violated in the fields {}'),
    'ZIP_SHP': _('The zip file is supported only if the following files are contained .shp, .dbf, .prj, .shx'),
}


class ValidationError(Exception):
    pass


class ImportValidator:
    def __init__(self, filepath_or_buffer, template, field_names=None, fixpos=False,
                 initial_as_default=True, label_as_colname=True, pass_warning=False, check_mimetype=True,
                 **kw_pandas_read):
        """
        Read the file (with existance/extension/type validation) and store in pandas dataframe (eventually build ModelForm from Model)
        :param filepath_or_buffer: filename/filepath string or file-like buffer
        :param template: Form or Model used as tabplate to validate file
        :param field_names: list of field_names used to create ModelForm from Model (default __all__)
        :param fixpos: Boolean, True to raise better header validation, only if file colums are exactly the same and in the same order of the Form fields
        :param initial_as_default, default True: use field inital value as default (only if required=Fasle)
        :param label_as_colname, default True: use field label as column name
        :param kw_pandas_read: pandas read_excel or read_csv arguments
            header : int, list of ints, default 0
                Row (0-indexed) to use for the column labels of the parsed DataFrame (and the start of the data). Use None if there is no header.
            skiprows : list-like or integer, default None
                Line numbers to skip (0-indexed) or number of lines to skip (int) at the start of the file.
            sheet_name : string, int, mixed list of strings/ints, or None, default 0
                Strings are used for sheet names, Integers are used in zero-indexed sheet positions.
                Lists of strings/integers are used to request multiple sheets.
                Specify None to get all sheets.
            sep : str, default ‘,’
                Delimiter to use in caharcater (eg comma) separated files.
        """

        self.fixpos = fixpos
        self.filter_cols = {}  # initialized by set_filters
        self.constants_fields = {}  # initialized by set_constant_fields
        self.extra_options = {}  # initialized by set_extra_options
        self.is_initialized = False
        self.header = kw_pandas_read.get('header', 0)
        self.sheet_name = kw_pandas_read.get('sheet_name', 0)
        self.skiprows = kw_pandas_read.get('skiprows', 0)
        self.file_err = []
        self.errors = None
        self.warnings = None
        self.unique_together = {}
        self.initial_as_default = initial_as_default
        self.label_as_colname = label_as_colname
        self.pass_warning = pass_warning
        self.filepath_or_buffer = filepath_or_buffer
        self.srid = None
        self.check_mimetype = check_mimetype
        self.kw_pandas_read = kw_pandas_read

        if issubclass(template, forms.BaseForm):
            self.form_class = template
        elif issubclass(template, models.Model):
            self.form_class = type(
                str('ModelForm{}'.format(template._meta.model_name)),
                (forms.ModelForm,),
                {'Meta': type(str('Meta'), (), {
                    'model': template,
                    'fields': field_names if field_names is not None else '__all__'
                })}
            )

    def __return_file_errors(self):
        return [{
            'pos': 'GENERALE',
            'field': 'File',
            'value': self.meta['filename'],
            'mess': m
        } for m in self.file_err]

    def set_filters(self, **kwargs):
        """
        :param kwargs: kwargs with field (column) to filter the data in the file (field_name=val_to_filter)
        :return:
        """

        if self.is_initialized:
            raise ValidationError(_('This operation can only be done before validating'))
        self.filter_cols = kwargs

    def set_constant_fields(self, **kwargs):
        """
        :param kwargs: kwargs with constants field to add in the form data (field_name=constant_val)
        :return:
        """

        if self.is_initialized:
            raise ValidationError(_('This operation can only be done before validating'))
        self.constants_fields = kwargs

    def set_extra_options(self, **kwargs):
        """

        :param kwargs: kwargs with extra option available inside form (as self.extra_options)
        :return:
        """
        if self.is_initialized:
            raise ValidationError(_('This operation can only be done before validating'))
        self.extra_options = kwargs

    def set_unique_together(self, unique_together):
        """
        :param unique_together: dict with two keys, 'errors', with list of list of fields, that raise an
                validation error, and 'warnings', with list of list of fields, that add ad warning.
                ex: unique_together {
                    'errors': [ ['field1', 'field2'], [.....], ... ],
                    'warnings': [ ['field1', 'field2'], [.....], ... ],
                }
        :return:
        """

        if self.is_initialized:
            raise ValidationError(_('This operation can only be done before validating'))
        self.unique_together = unique_together

    def _base_validation(self):
        """
        Perform file level (mainly header) validation
        :return: return nothing, only append to errors dict the file level errors
        """

        if self.file_err:
            return

        # # read form labels and inits # #
        # field_names = list(form_class.base_fields)
        # field_label = [f.label.lower().strip() for f in self.form_class()]
        field_label = []
        field_decod = OrderedDict()  # map {field_name: field_label.strip()}
        header_encode = OrderedDict()  # map {col_slug =[slugify(field_label)]: field_name}
        field_initials = {}
        # for fname in set(self.form_class.base_fields) - set(self.constants_fields):
        geometry_field = None

        for fname, field in self.form_class().fields.items():
            if fname not in list(self.constants_fields):
                flabel = (field.label if self.label_as_colname else None) or fname
                col_slug = slugify(flabel)
                field_label.append(col_slug)  # flabel.lower().strip()
                field_decod[fname] = flabel.strip()  # used only in error report keys/message
                header_encode[col_slug] = fname  # used to rename dataframe columns in preprocess
                if field.initial is not None and not field.required:
                    field_initials[fname] = field.initial

            if issubclass(field.__class__, forms.GeometryField):
                # TODO if flabel not in self.df_rows.columns (latrimenti aggiungo colonna geometryb per excel con wkt)
                if 'geometry' not in self.df_rows.columns:
                    self.df_rows['geometry'] = 'POLYGON EMPTY'


        nfields = len(field_label)
        self.field_decod = field_decod

        # # check empty # #
        if self.df_rows.empty:
            self.file_err.append(ERR_MSG['NODATA'].format(self.sheet_name + 1))
        # # check headers # #
        elif self.header is not None:
            # # normalize column names (lower and strip) -> slugify
            # norm_header = map(lambda x: str(x).lower().strip(), self.df_rows.columns)
            # norm_header = OrderedDict([(h, h.lower().strip()) for h in self.df_rows.columns])
            norm_header = OrderedDict([(h, slugify(h)) for h in self.df_rows.columns])
            self.df_rows.rename(columns=norm_header, inplace=True)

            # TODO check for unamed columns, forse non è necessario
            # unamed_cols = self.df_rows.columns.str.startswith('unnamed')
            # if any(unamed_cols):
            #     unameds = ', '.join([xlcolname(nc) for nc, u in enumerate(unamed_cols) if u])
            #     self.file_err.append(ERR_MSG['UNAMED_COLS'].format(unameds))
            # if self.file_err:
            #     return return

            # TODO check duplicated columns
            # if not selffixpos and any(df_rows.columns.duplicated())
            #     self.file_err.append(ERR_MSG['HEADER'].format(1))
            # if self.file_err:
            #     return return

            if not self.fixpos:
                if self.df_rows.shape[1] < nfields:
                    self.file_err.append(ERR_MSG['LESS_COLS'].format(self.df_rows.shape[1], nfields))
                if not set(field_label).issubset(list(norm_header.values())):
                    self.file_err.append(ERR_MSG['HEADER'].format(self.header + self.skiprows + 1))
                    col_diffs = ~pd.Series(field_label).isin(list(norm_header.values()))
                    for nc, diff in enumerate(col_diffs):
                        if diff:
                            self.file_err.append(ERR_MSG['COLUMN'].format(
                                # field_label[nc],
                                list(field_decod.values())[nc],
                            ))
            elif self.fixpos:
                if self.df_rows.shape[1] < nfields:
                    self.file_err.append(ERR_MSG['LESS_COLS'].format(self.df_rows.shape[1], nfields))
                    self.file_err.append(ERR_MSG['HEADER'].format(self.header + self.skiprows + 1))
                    col_diffs = ~pd.Series(field_label).isin(list(norm_header.values()))
                    for nc, diff in enumerate(col_diffs):
                        if diff:
                            self.file_err.append(ERR_MSG['COLUMN'].format(
                                # field_label[nc],
                                list(field_decod.values())[nc],
                            ))
                elif not field_label == list(norm_header.values())[:nfields]:
                    self.file_err.append(ERR_MSG['HEADER'].format(self.header + self.skiprows + 1))
                    col_diffs = ~(pd.Series(field_label) == list(norm_header.values())[:nfields])
                    for nc, diff in enumerate(col_diffs):
                        if diff:
                            self.file_err.append(ERR_MSG['COL_POS'].format(
                                nc + 1,
                                xlcolname(nc),
                                # field_label[nc],
                                list(field_decod.values())[nc],
                                list(norm_header.keys())[nc],
                            ))

        else:  # no header: positional mode
            ncols = self.df_rows.shape[1]
            if ncols < nfields:
                self.file_err.append(ERR_MSG['LESS_COLS'].format(ncols, nfields, '\', \''.join(field_label)))

        if self.file_err:
            return

        # #  preprocess dataframe   # #
        # # rename header
        if self.header is not None:
            # slice dataframe to form columns and rename column to fields name
            if self.fixpos:
                self.df_rows = self.df_rows.iloc[:, :nfields]
            else:
                self.df_rows = self.df_rows[field_label]
            self.df_rows.rename(columns=header_encode, inplace=True)
        else:  # no header: positional mode
            self.df_rows = self.df_rows.iloc[:, :nfields]
            self.df_rows.columns = list(header_encode.values())

        # # insert default values
        if self.initial_as_default and field_initials:
            for col, val in field_initials.items():
                self.df_rows.fillna(value={col: val}, inplace=True)

        # # format dates
        # TODO forzare casting a date delle colonne dichiarate come date fields nel from
        # To re-infer data dtypes for object columns, use DataFrame.infer_objects()
        # For all other conversions use the data-type converters pd.to_datetime, pd.to_timedelta and pd.to_numeric.
        # pd.to_datetime(self.df_rows[date_col], infer_datetime_format=True, errors='coerce')
        for date_col in self.df_rows.infer_objects().select_dtypes(include=['datetime64']).columns:
            self.df_rows[date_col] = self.df_rows[date_col].dt.strftime('%Y-%m-%d')
            self.df_rows[date_col].replace({'NaT': ''}, inplace=True)

        # # fill NaN (and dates NaT) with '' (otherwise initialize form with nan string)
        self.df_rows.replace([np.nan, pd.NaT], ['', ''], inplace=True)
        # could not rplace with None because pandas try to chage dtype to float
        # self.df_rows.replace([np.nan, pd.NaT], [None, None], inplace=True)

        # # filter dataframe by kwargs (session)
        # filter_cols = list(self.kwargs)
        # TODO check che var dichiarate il filter siano nel form: raise diretto
        # do_filter = pd.Series(filter_cols).isin(self.df_rows.columns)
        # if any(filters):
        #   for do,fcol in zip(do_filter,filter_cols):
        #     if do:
        #       #print do,fcol
        #       self.df_rows = self.df_rows[df_rows[fcol]==self.kwargs[fcol]]
        # do_filter = pd.Series(filter_cols).isin(self.df_rows.columns)
        for fcol, fval in self.filter_cols.items():
            # self.df_rows = self.df_rows[self.df_rows[fcol] == fval]
            if not isinstance(fval, list):
                fval = [fval]
            self.df_rows = self.df_rows[self.df_rows[fcol].isin(fval)]

        self.is_initialized = True

    def _validate_row(self, row_dict, save=False):
        """
        Instantiate the form with the row data and validate it
        :param row_dict: dict with the fields:value to initialize the form instance
        :param save: Boolean, if True save the validated form
        :return: return nothing, only append to errors dict the specific row (form instance) errors
        """

        # inject constants_fields (set by set_constants_fields) in the dict that initializes the form values
        row_dict.update(self.constants_fields)
        # initialize the form, instantiating the class with the values
        form = self.form_class(row_dict)
        # inject extra_options (set by set_extra_options) in the form (you can access it as self.extra_options)
        if True:  # self.extra_options: I put them in the form even if empty {}, so I don't have to check if they exist
            form.extra_options = self.extra_options
        # valido e salvo il form
        if form.is_valid():
            if save and hasattr(form, 'save') and callable(form.save):
                return form.save()
            elif not save and hasattr(form, 'save') and callable(form.save):
                if 'commit' in inspect.getfullargspec(form.save).args:
                    return form.save(commit=False)
        else:
            # row_err = {}
            # for k, v in form.errors.items():
            #     row_err[self.field_decod[k]] = v
            # self.errors.append({
            #     'pos': row_dict['Index'] + (2 if self.header is not None else 1),
            #     'err': row_err
            # })
            for field, mess in form.errors.items():
                self.errors.extend([{
                    'pos': row_dict['Index'] + (self.header + 2 if self.header is not None else 1) + self.skiprows,
                    'field': self.field_decod.get(field, 'OTHER'),  # 'COMPLESSIVO' if field == '__all__' else self.field_decod[field],
                    'value': form.data.get(field, None),  # if field != '__all__' else None
                    'mess': m
                } for m in mess])

    def postprocess_record(self, instance, save):
        """

        :param instance: is wathever returned by form save method
        :param save: Boolean is the importer save option
        """
        pass

    def _unique_together_check(self):
        if self.unique_together is not None:
            # error part
            if 'errors' in self.unique_together:
                errors_unique = self.unique_together['errors']
                for er in errors_unique:
                    if type(er) == list:
                        df_tmp = self.df_rows[er].astype(str)
                        for index, duplicated in df_tmp.duplicated(subset=er, keep=False).items():
                            if duplicated:
                                self.errors.append({
                                    'pos': index + (self.header + 2 if self.header is not None else 1) + self.skiprows,
                                    'field': ' - '.join(er),
                                    'value': '',
                                    'mess': ERR_MSG['UNIQ_VIOLATION'].format(' - '.join(er))
                                })
            # warning part
            if 'warnings' in self.unique_together:
                warnings_unique = self.unique_together['warnings']
                for war in warnings_unique:
                    if type(war) == list:
                        df_tmp = self.df_rows[war].astype(str)
                        for index, duplicated in df_tmp.duplicated(subset=war, keep=False).items():
                            if duplicated:
                                self.warnings.append({
                                    'pos': index + (self.header + 2 if self.header is not None else 1) + self.skiprows,
                                    'field': ' - '.join(war),
                                    'value': '',
                                    'mess': ERR_MSG['UNIQ_VIOLATION'].format(' - '.join(war))
                                })

    def get_dataframe(self):

        if not hasattr(self, 'df_rows') or self.df_rows is None:
            mime = magic.Magic(mime=True, uncompress=True)  # uncompress, otherwise xlsx is zip
            mimetype = None
            ext = None
            filename = None

            if not self.file_err:
                if not self.filepath_or_buffer:
                    self.file_err.append(ERR_MSG['NOFILE'])

            if not self.file_err:
                if isinstance(self.filepath_or_buffer, InMemoryUploadedFile):
                    # https://docs.djangoproject.com/en/2.1/_modules/django/core/files/uploadedfile/
                    mimetype = self.filepath_or_buffer.content_type
                    ext = os.path.splitext(self.filepath_or_buffer.name)[-1].lower().lstrip('.')
                    filename = self.filepath_or_buffer.name
                elif not hasattr(self.filepath_or_buffer, 'read') \
                    and os.path.exists(self.filepath_or_buffer) \
                    and os.path.isfile(self.filepath_or_buffer):
                    mimetype = mime.from_file(self.filepath_or_buffer)
                    ext = os.path.splitext(self.filepath_or_buffer)[-1].lower().lstrip('.')
                    filename = self.filepath_or_buffer
                elif hasattr(self.filepath_or_buffer, 'read'):
                    mimetype = mime.from_buffer(self.filepath_or_buffer.read())
                    filename = 'buffer'
                else:
                    self.file_err.append(ERR_MSG['WRONG_FILE'].format(self.filepath_or_buffer))

            self.meta = {
                'filename': filename,
                'sheet': self.sheet_name + 1 if type(self.sheet_name) == int else self.sheet_name
            }

            if not self.file_err:
                if ext and ext not in list(MIME):
                    self.file_err.append(ERR_MSG['WRONG_EXT'].format(ext, ', '.join(list(MIME))))

            if not self.file_err:
                # read with dtype='object' to allow mixed dtype columns, prevent pandas to autocast (eg int with NaN to float)
                if ext in ['xls', 'xlsx'] and \
                    (self.check_mimetype is False or (mimetype in MIME['xls'] or mimetype in MIME['xlsx'])):
                    self.df_rows = pd.read_excel(self.filepath_or_buffer, dtype='object', **self.kw_pandas_read)
                elif ext in ['csv', 'txt'] and \
                    (self.check_mimetype is False or (mimetype in MIME['csv'] or mimetype in MIME['txt'])):
                    try:
                        # check nrighe se usa skiprows, pandas si spacca se uso skiprows=1 ma c'è una sola riga
                        self.df_rows = pd.read_csv(self.filepath_or_buffer, dtype='object', **self.kw_pandas_read)
                    except pd.errors.EmptyDataError:
                        self.file_err.append(ERR_MSG['NODATA'].format(self.sheet_name + 1))
                    except pd.errors.ParserError as e:
                        self.file_err.append(ERR_MSG['PARSE_ERR'].format(
                            self.kw_pandas_read.get('sep', self.kw_pandas_read.get('delimiter', ',')), e))
                elif ext in ['zip'] and \
                    (self.check_mimetype is False or (mimetype in MIME['zip'])):
                    # decomprimere tutto in temp dir e poi leggere con geopadas
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # raise Exception(filepath_or_buffer, type(filepath_or_buffer), filepath_or_buffer.read())
                        zp = zipfile.ZipFile(self.filepath_or_buffer)
                        core_file = ''
                        files_ext_necessary = ['shp', 'dbf', 'prj', 'shx']
                        files_ext = []
                        all_files = True

                        for name in zp.namelist():
                            ext_file = os.path.splitext(name)[-1].lower().lstrip('.')
                            files_ext.append(ext_file)
                            if ext_file == 'shp':
                                core_file = tmpdir + '/' + name
                            zp.extract(name, tmpdir)

                        zp.close()
                        for ex in files_ext_necessary:
                            if ex not in files_ext:
                                all_files = False

                        if core_file != '' and all_files:
                            df_rows = geopandas.read_file(core_file)
                            self.srid = df_rows.crs.to_epsg()
                            str_csv = df_rows.to_csv(index=False)
                            str_csv = str_csv.replace('.0,', ',')
                            self.df_rows = pd.read_csv(io.StringIO(str_csv), dtype='object')
                            # convert wkt to ewkt
                            # self.df_rows['geometry'] = 'SRID=' + str(self.srid) + ';' + self.df_rows['geometry'].astype(str)
                            # FIX: changed to a LAMBDA because sometimes it requires too much ram to do the astype
                            self.df_rows['geometry'] = self.df_rows['geometry'].apply(lambda x: 'SRID=' + str(self.srid) + ';' + x)

                        else:
                            self.file_err.append(ERR_MSG['ZIP_SHP'])
                else:
                    self.file_err.append(ERR_MSG['WRONG_TYPE'].format(mimetype))

    def _validate_rows(self, save=False):
        """
        Loop over each file/dataframe rows and run the row validation (_validate_row)
        :param save: Boolean, if True save the validated form
        :return: Boolean: False if no row has errors
        """

        self.errors = []
        self.warnings = []
        # insert unique_together as control
        self._unique_together_check()

        for row in self.df_rows.itertuples(index=True, name='Row'):
            row_dict = row._asdict()
            instance = self._validate_row(row_dict, save=save)
            self.postprocess_record(instance, save)

        if self.pass_warning or save:
            return len(self.errors) == 0
        else:
            return len(self.errors) == 0 and len(self.warnings) == 0
        # for nr,row_dict in enumerate(iter(df_rows.to_dict(orient='record'))):
        #   nr+=1
        #   # print nr,row_dict
        #   errors_row = validate_row(form_class,row_dict,save)
        #   if len(errors_row)>0:
        #     errors['rows'][nr] = errors_row

    def validate(self, save=None):
        """
        Run the file validation, file level validation (_base_validation) and then each row validation (_validate_rows)
        :param save: None|'ROW'|'FULL'
            None: default, don't save nothiong
            ROW: save each valid row after the form validation
            FULL: save all at the end, only in all the rows are validated without errors
        :return: {valid:True/False, errors:[item_error_dict], nerrors: number_of_errors, meta: infile_metadata}
            con item_error_dict={pos: row_number_or_other_position, field: field_name, mess: error_message}
        """

        self.get_dataframe()

        if not self.is_initialized:
            self._base_validation()

        if self.file_err:
            self.errors = self.__return_file_errors()
            self.warnings = []
            return {'valid': False,
                    'errors': self.errors,
                    'nerrors': len(self.errors),
                    'warnings': self.warnings,
                    'nwarnings': len(self.warnings),
                    'meta': self.meta}

        if save and save not in ['ROW', 'FULL']:
            raise TypeError(_('Validate save mode are ROW | FULL'))

        if save is None:
            valid = self._validate_rows(save=False)

        elif save == 'ROW':
            valid = self._validate_rows(save=True)

        elif save == 'FULL':
            if self._validate_rows(save=False):
                valid = self._validate_rows(save=True)
            else:
                valid = False

        file_saved = None

        if not valid:
            if self.pass_warning and len(self.errors) == 0:
                self.warnings = []
                valid = True
            elif not self.pass_warning and len(self.warnings) > 0 and len(self.errors) == 0:
                # salvo il file
                file_saved = ImportFile(allegato=self.filepath_or_buffer)
                file_saved.save()

        return {'valid': valid,
                'errors': self.errors,
                'nerrors': len(self.errors),
                'warnings': self.warnings,
                'nwarnings': len(self.warnings),
                'meta': self.meta,
                'id_file': file_saved.id if file_saved is not None else None}


class ImportValidatorAppendOut(ImportValidator):
    def validate(self, save=None):
        self.buffer = []
        return super(ImportValidatorAppendOut, self).validate(save)

    def postprocess_record(self, instance, save):
        if instance:
            self.buffer.append(instance)
