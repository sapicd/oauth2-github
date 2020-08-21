picbed-oauth2-github
====================

这是基于 `picbed <https://github.com/staugur/picbed>`_ 的一个小的扩展模块，
用来接入 GitHub OAuth2 登录。

安装
------

- 正式版本

    `$ pip install -U picbed-oauth2-github`

- 开发版本

    `$ pip install -U git+https://github.com/staugur/picbed-oauth2-github.git@master`

开始使用
----------

此扩展请在部署 `picbed <https://github.com/staugur/picbed>`_ 图床后使用，需要
其管理员进行添加扩展、设置钩子等操作。

添加：
^^^^^^^^

请在 **站点管理-钩子扩展** 中点击安装第三方包，可在弹窗列表中选择
picbed-oauth2-github，点击行尾图标，或者在弹窗底部按照正式/开发版本填写安装。

安装完成后，在 **站点管理-钩子扩展**  中点击添加第三方钩子，
输入名称： ``oauth2gh`` ，确认后提交即可加载这个模块。

配置：
^^^^^^^^

在 **站点管理-网站设置** 底部的钩子配置区域配置GitHub OAuth ID和
GitHub OAuth Secret！

使用：
^^^^^^^^

1、在GitHub中 `注册一个OAuth App <https://github.com/settings/applications/new>`_

Authorization callback URL是picbed地址，比如http://demo.picbed.pro

其他参数根据实际填写。

提交后生成的Client ID和Client Secret是需要配置到picbed中的。

2、在picbed **站点管理-网站设置** 底部钩子配置区域中选择第三方认证为
oauth2gh即可。

启用后，在登录页面会显示使用GitHub登录，跳转到授权页，授权后跳回picbed。

PS：

- 登录状态是依靠session

- 用户名有 **gh-** 前缀
