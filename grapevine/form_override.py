from flask_security.forms import RegisterForm, ConfirmRegisterForm, Required, PasswordConfirmFormMixin
from wtforms import StringField


class RegisterFormWithNames(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])


class ConfirmRegisterFormWithNames(ConfirmRegisterForm, PasswordConfirmFormMixin):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])

