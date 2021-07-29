# from flask_jwt_extended import create_access_token, create_refresh_token

# project resources
from authentication.models import UserLoginInfo
from utils.common import generate_response
from utils.http_code import *
import datetime
import random
from utils.jwt.jwt_security import JwtAuth
import os

expiry = datetime.timedelta(days=5)


def login_user(request, input_data):
    try:
        user = UserLoginInfo.objects.get(email=input_data.get('email').lower())
    except:
        return generate_response(message='No record found with this email, please signup first.')
    auth_success = user.check_pw_hash(input_data.get('password'))
    if not auth_success:
        return generate_response(message='Email or password you provided is invalid. please check it once',
                                 status=HTTP_401_UNAUTHORIZED)
    else:
        # access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
        # refresh_token = create_refresh_token(identity=str(user.id))

        access_token, refresh_token = get_refresh_access_token(request, user)
        return generate_response(data={'access_token': access_token,
                                       'refresh_token': refresh_token,
                                       'logged_in_as': f"{user.email}",
                                       'meta': user.to_json()
                                       }, status=HTTP_200_OK)


def social_login(request, input_data):
    try:
        user = UserLoginInfo.objects.get(email=input_data['email'].lower())
    except:
        user = UserLoginInfo(**input_data)
        # provider random default password
        user.password = str(random.randint(10000000, 99999999))
    errors = user.clean()
    if errors:
        return errors
    if 'social_id' not in input_data or not input_data['social_id']:
        return generate_response(message='Social id is missing or invalid.')

    user.email = input_data['email'].lower()
    user.role = input_data['role']
    user.auth_type = input_data['auth_type']
    user.social_id = input_data['social_id']
    user.is_active = True
    user.is_verified = True
    # if input_data['role'] == B2B_USER:
    #     user.parent = self.input_data['parent']
    user.save()

    access_token, refresh_token = get_refresh_access_token(request, user)
    return generate_response(data={'access_token': access_token,
                                   'refresh_token': refresh_token,
                                   'logged_in_as': f"{user.email}",
                                   'meta': user
                                   }, status=HTTP_200_OK)


def update_user(input_data, user):
    if 'name' in input_data or input_data['name']:
        user.name = input_data['name']
    if 'phone' in input_data or input_data['phone']:
        user.name = input_data['phone']
    if 'profile_image' in input_data or input_data['profile_image']:
        user.name = input_data['profile_image']
    if 'is_active' in input_data:
        user.is_active = True
    return generate_response(data=user.id, message='User updated', status=HTTP_200_OK)


def get_refresh_access_token(request, user):
    Jwt = JwtAuth(os.environ.get('VERIFY_TOKEN'))
    response = {
        'id': str(user.id), 'email': user.email,
        'auth_type': user.auth_type,
    }
    return Jwt.encode(response, request, user)