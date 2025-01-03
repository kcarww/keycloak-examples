from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
import random
import string
from urllib.parse import urlencode
import requests
import jwt

class LoginView(APIView):
    def get(self, request):
        nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        request.session['nonce'] = nonce
        request.session['state'] = state

        login_params = {
            'client_id': 'test-client',
            'redirect_uri': 'http://localhost:8000/api/callback/',
            'response_type': 'code',
            'scope': 'openid',
            'nonce': nonce,
            'state': state,
        }

        url = f"http://localhost:8080/realms/teste-realm/protocol/openid-connect/auth?{urlencode(login_params)}"
        return Response({'url': url})


class LogoutView(APIView):
    def get(self, request):
        id_token = request.session.get('id_token')

        logout_params = {
            'id_token_hint': id_token,
            'post_logout_redirect_uri': 'http://localhost:8000/api/login/',
        }

        url = f"http://localhost:8080/realms/fullcycle-realm/protocol/openid-connect/logout?{urlencode(logout_params)}"
        request.session.flush()  
        return Response({'url': url})
    


class CallbackView(APIView):
    def get(self, request):
        state = request.session.get('state')
        nonce = request.session.get('nonce')

        if request.query_params.get('state') != state:
            raise AuthenticationFailed('Unauthenticated')

        code = request.query_params.get('code')

        body_params = {
            'client_id': 'fullcycle-client',
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://localhost:8000/api/callback/',
        }

        url = 'http://localhost:8080/realms/teste-realm/protocol/openid-connect/token'
        response = requests.post(url, data=body_params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

        if response.status_code != 200:
            raise AuthenticationFailed('Token request failed')

        result = response.json()

        payload_access_token = jwt.decode(result['access_token'], options={"verify_signature": False})
        payload_id_token = jwt.decode(result['id_token'], options={"verify_signature": False})

        if payload_access_token['nonce'] != nonce:
            raise AuthenticationFailed('Unauthenticated')

        request.session['user'] = payload_access_token
        request.session['access_token'] = result['access_token']
        request.session['id_token'] = result['id_token']

        return Response({'message': 'Authenticated', 'user': payload_access_token})

class AdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.session.get('user')
        if not user:
            return Response({'message': 'Unauthenticated'}, status=401)
        return Response({'user': user})