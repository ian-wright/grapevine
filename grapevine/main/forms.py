from flask_security.forms import RegisterForm, ConfirmRegisterForm, Required, \
    PasswordConfirmFormMixin, Form, UserEmailFormMixin, EmailFormMixin
from wtforms import StringField, SubmitField


# override flask-security registration form
class RegisterFormWithNames(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])


# override flask-security confirmable registration form
class ConfirmRegisterFormWithNames(ConfirmRegisterForm, PasswordConfirmFormMixin):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])



