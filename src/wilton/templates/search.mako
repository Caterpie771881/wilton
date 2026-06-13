<%inherit file="base.mako"/>

<%block name="title">搜索结果</%block>

<%block name="main">
<div id="mainbar">
    <h1>搜索结果</h1>
    <div id="results"><div>正在导入资源...</div></div>
</div>
${sidebar}
</%block>

<%block name="script">
<script type="module">
    import { getSearchResults } from "${ctx.config.website_address}/js/search-page.js";

    const urlParams = new URLSearchParams(window.location.search);
    const keyword = urlParams.get("q");

    getSearchResults(keyword);
</script>
</%block>
