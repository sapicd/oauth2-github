# -*- coding: utf-8 -*-
"""
    oauth2gh
    ~~~~~~~~

    OAuth2 for GitHub.

    :copyright: (c) 2020 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

__version__ = '0.1.0'
__author__ = 'staugur <staugur@saintic.com>'
__description__ = '通过GitHub OAuth认证'
__appversion__ = '1.9.0-rc'
__hookname__ = 'oauth2gh'

from flask import g, url_for, redirect, abort, request, session
from utils.web import try_proxy_request, set_site_config
from utils.exceptions import PageError


site_auth = True

intpl_login_area = '''
{% if g.site.site_auth == "oauth2gh" %}
<a href="{{ url_for('front.ep', hook_name='oauth2gh', route_name='authorize') }}"
style="display:block;float:left;">
<i class="saintic-icon saintic-icon-github"></i> 使用GitHub登录
</a>
{% endif %}
'''

intpl_hooksetting = '''
<div class="layui-row">
<div class="layui-col-xs12 layui-col-sm12 layui-col-md6">
<div class="layui-form-item">
    <label class="layui-form-label">
        <b style="color: red;">*</b> GitHub OAuth ID
    </label>
    <div class="layui-input-block">
        <input type="text" name="oauth2gh_client_id"
            value="{{ g.site.oauth2gh_client_id }}"
            placeholder="GitHub OAuth App Client ID"
            autocomplete="off" class="layui-input">
    </div>
</div>
</div>
<div class="layui-col-xs12 layui-col-sm12 layui-col-md6">
<div class="layui-form-item">
    <label class="layui-form-label">
        <b style="color: red;">*</b> GitHub OAuth Secret
    </label>
    <div class="layui-input-block">
        <input type="text" name="oauth2gh_client_secret"
            value="{{ g.site.oauth2gh_client_secret }}"
            placeholder="GitHub OAuth App Client Secret"
            autocomplete="off" class="layui-input">
    </div>
</div>
</div>
</div>
'''


def authorize():
    client_id = g.cfg.oauth2gh_client_id
    if client_id and g.cfg.site_auth == "oauth2gh":
        return redirect(
            "https://github.com/login/oauth/authorize" +
            "?client_id={}&redirect_uri={}&state=picbed".format(
                client_id,
                url_for(
                    "front.ep", hook_name=__hookname__, route_name="callback",
                    _external=True
                )
            )
        )
    else:
        return abort(404)


def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    client_id = g.cfg.oauth2gh_client_id
    client_secret = g.cfg.oauth2gh_client_secret
    if g.cfg.site_auth != "oauth2gh":
        return abort(404)
    if code and state == "picbed" and client_id and client_secret:
        #: 登录授权成功
        try:
            resp = try_proxy_request(
                "https://github.com/login/oauth/access_token",
                data=dict(
                    client_id=client_id, client_secret=client_secret, code=code
                ),
                headers=dict(Accept="application/json"),
            )
        except (ValueError, TypeError, Exception):
            raise PageError("换取AccessToken失败，请稍后重试！", 403)
        else:
            data = resp.json()
            if "error" in data:
                raise PageError(data["error_description"], 403)
            token = data["access_token"]
            set_site_config(dict(oauth2gh_token=token))
            #: 获取用户信息
            try:
                resp = try_proxy_request(
                    "https://api.github.com/user",
                    method="get",
                    headers=dict(Authorization="token {}".format(token)),
                )
            except (ValueError, TypeError, Exception):
                raise PageError("拉取用户信息失败，请稍后重试！", 403)
            data = resp.json()
            email = data.get("email")
            #: 设置登录态 TODO 系统已存在username
            session.update(
                signin=True,
                userinfo=dict(
                    username="gh-" + data["login"],
                    avatar=data.get("avatar_url"),
                    nickname=data.get("name"),
                    email=email,
                    email_verified=1 if email else 0,
                )
            )
            return redirect(url_for("front.index"))
    else:
        return abort(403)


def route():
    return dict(
        authorize=authorize,
        callback=callback,
    )


def logout_handler():
    session.pop("signin", None)
    session.pop("userinfo", None)


def before_request():
    if g.signin is False and session.get("signin"):
        g.signin = True
        g.userinfo = session["userinfo"]


def profile_update(**kwargs):
    userinfo = session["userinfo"]
    userinfo.update(kwargs)
    session.update(userinfo=userinfo)
