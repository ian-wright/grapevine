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


# class InviteUserEmailForm(Form, UserEmailFormMixin):
#
#     # submit = SubmitField('Add a friend.')
#
#     def validate(self):
#         print("validating existing user email form for friend invite...")
#         return super(InviteUserEmailForm, self).validate()
#
#
# class InviteEmailForm(Form, EmailFormMixin):
#
#     # submit = SubmitField('Add a friend.')
#
#     def validate(self):
#         print("validating new user email form for friend invite...")
#         return super(InviteEmailForm, self).validate()


