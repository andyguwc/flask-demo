# -*- coding: utf-8 -*-
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, TextAreaField, HiddenField
# from wtforms.validators import DataRequired, Optional, Length


# class CreditCardForm(FlaskForm):
#     stripe_key = HiddenField('Stripe publishable key',
#                              [DataRequired(), Length(1, 254)])
#     plan = HiddenField('Plan',
#                        [DataRequired(), Length(1, 254)])
#     coupon_code = StringField('Do you have a coupon code?',
#                               [Optional(), Length(1, 128)])
#     name = StringField('Name on card',
#                        [DataRequired(), Length(1, 254)])


# class UpdateSubscriptionForm(FlaskForm):
#     pass


# class CancelSubscriptionForm(FlaskForm):
#     pass