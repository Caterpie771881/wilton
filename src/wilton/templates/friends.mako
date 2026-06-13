<%inherit file="base.mako"/>

<%block name="title">${ctx.config.title.main} - 友情链接</%block>

<%block name="main">
<div id="mainbar" class="no-side-bar">
    <h1>友情链接</h1>
    % for group in config:
    <h2>${group}</h2>
    <div class="link-group">
        % for info in config[group]:
        <div class="link-card">
            <h3>${info.name}</h3>
            <a href="${info.link}">${info.link}</a>
            <p title="${info.desc}">${info.desc}</p>
        </div>
        % endfor
        % if len(config[group]) % 3 == 2:
        <div class="link-card" style="margin: 0px"></div>
        % endif
    </div>
    % endfor
</div>
</%block>
