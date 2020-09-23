# -*- coding: utf-8 -*-
from flask import current_app, url_for, request, redirect, session
from flask_login import current_user, login_user, logout_user, login_required
from requests_oauthlib import OAuth2Session

"""
Define OAuth objects
"""


class OAuthSignIn(object):
    """Wrapper around OAuth providers to provide consistent interface
    """
    def __init__(
            self, 
            provider_name, 
            authorization_base_url, 
            token_url, 
            **kwargs):
        self.provider_name = provider_name
        self.authorization_base_url = authorization_base_url
        self.token_url = token_url
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']

    def authorize(self):
        """Request to the oauth endpoint
        """
        raise NotImplementedError()

    def callback(self):
        """Saves token in session and extract user information
        """
        raise NotImplementedError()

    def get_callback_url(self):
        """Get callback URL, certain providers require it 
        """
        return url_for(
            'auth.oauth_callback', 
            provider=self.provider_name, 
            _external=True)


class GithubSignIn(OAuthSignIn):
    def __init__(self, **kwargs):
        super().__init__(
            provider_name='github',
            authorization_base_url='https://github.com/login/oauth/authorize',
            token_url='https://github.com/login/oauth/access_token',
            **kwargs)
    
    def authorize(self):
        github = OAuth2Session(self.client_id, scope='read:user user:email')
        authorization_url, state = github.authorization_url(self.authorization_base_url)
        session['github_oauth_state'] = state
        return redirect(authorization_url)

    def callback(self):
        github = OAuth2Session(
            self.client_id, 
            state=session['github_oauth_state'])
        # obtain token by parsing the request code and call the token url
        token = github.fetch_token(
            self.token_url, 
            client_secret=self.client_secret,
            authorization_response=request.url)
        session['github_oauth_token'] = token

        # make another request with token to obtain user data
        github = OAuth2Session(self.client_id, token=token)
        me = github.get('https://api.github.com/user').json()
        return me['email'], me['login']


class GoogleSignIn(OAuthSignIn):
    def __init__(self, **kwargs):
        super().__init__(
            provider_name='google',
            authorization_base_url='https://accounts.google.com/o/oauth2/auth',
            token_url='https://accounts.google.com/o/oauth2/token',
            **kwargs
        )

    def authorize(self):
        google = OAuth2Session(
            self.client_id, 
            scope = [
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
            redirect_uri=self.get_callback_url())

        authorization_url, state = google.authorization_url(
            self.authorization_base_url,
            access_type="offline", prompt="select_account")

        session['google_oauth_state'] = state
        return redirect(authorization_url)

    def callback(self):
        google = OAuth2Session(
            self.client_id,
            redirect_uri=self.get_callback_url(),
            state=session['google_oauth_state']
        )
        token = google.fetch_token(
            self.token_url, 
            client_secret=self.client_secret,
            authorization_response=request.url)
    
        google = OAuth2Session(self.client_id, token=token)
        me = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        return me['email'], me['email'].split('@')[0]


provider_class_map = {
    'github': GithubSignIn,
    'google': GoogleSignIn
}