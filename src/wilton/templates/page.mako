<%inherit file="base.mako"/>

<%block name="title">${ctx.config.title.main} - ${page.title}</%block>

<%block name="main">
<div id="mainbar">
    ${page.content}
</div>
${sidebar}
</%block>
