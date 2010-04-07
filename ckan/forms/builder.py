import formalchemy
from pylons.templating import render
from pylons import c

from ckan import model
import common

class CkanFieldset(formalchemy.FieldSet):
    def render(self, **kwargs):
        if hasattr(self, 'form_template') and self.form_template is not None:
            c.fieldset = self
            return render(self.form_template)
        else:
            return formalchemy.FieldSet(self, **kwargs)

    def get_field_groups(self):
        groups = []
        for field in self.render_fields.values():
            group = field.metadata.get('field_group', '')
            if group not in groups:
                groups.append(group)
        return groups


class FormBuilder(object):
    '''Builds form fieldsets'''
    def __init__(self, base_object):
        self.fs = CkanFieldset(base_object)
        self.added_fields = []
        self.options = self.fs._fields # {field_name:fs.field}
        self.includes = None

    def add_field(self, field):
        if isinstance(field, common.ConfiguredField):
            field = field.get_configured()
        assert isinstance(field, formalchemy.Field), field
        self.fs.append(field)

    def set_field_option(self, field_name, option, *args):
        field = self.options[field_name]
        assert field
        option = getattr(field, option)
        if isinstance(args[0], dict):
            self.options[field_name] = option(**args[0])
        else:
            self.options[field_name] = option(*args)

    def set_field_text(self, field_name, label=None, instructions=None, hints=None):
        if label:
            self.set_field_option(field_name, 'label', label)
        if instructions:
            self.set_field_option(field_name, 'with_metadata', {'instructions':instructions})
        if hints:
            self.set_field_option(field_name, 'with_metadata', {'hints':hints})

##    def set_label_hidden(self, field_name):
##        self.set_field_option(field_name, 'with_metadata', {'hidden_label':True})

    def set_displayed_fields(self, field_name_list):
        assert isinstance(field_name_list, (list, tuple))
        self.includes = field_name_list
        self.focus = self.fs._fields[field_name_list[0]]

    def set_displayed_fields_in_groups(self, groups_dict):
        assert isinstance(groups_dict, dict)
        all_field_names = []
        for group_name, field_names in groups_dict.items():
            assert isinstance(group_name, (str, unicode))
            assert isinstance(field_names, (list, tuple))
            for field_name in field_names:
                assert isinstance(field_name, str)
                self.set_field_option(field_name, 'with_metadata', {'field_group':group_name})
            all_field_names += field_names
        self.set_displayed_fields(all_field_names)

    def set_label_prettifier(self, prettify):
        '''@prettify function that munges field labels'''
        self.fs.prettify = prettify

    def set_form_template(self, template_path):
        self.fs.form_template = template_path

    def get_fieldset(self):
        self.fs.configure(options=self.options.values(),
                          include=[getattr(self.fs, name) for name in self.includes],
                          focus=self.focus)
        return_fs = self.fs
        self.fs = None # can't run this method again
        return return_fs