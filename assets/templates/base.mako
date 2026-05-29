<%def name="make_links(latex, image)">
    <link rel="stylesheet" href="${website_address}/css/wilton.css" />
    % if latex:
    <link defer rel="stylesheet" href="${website_address}/css/katex.min.css" />
    % endif
    % if image:
    <link defer rel="stylesheet" href="${website_address}/css/fancybox.css" />
    % endif
</%def>

<%def name="make_scripts(codeblock, latex, image)">
    <script src="${website_address}/js/wilton.js"></script>
    % if codeblock:
    <script defer src="${website_address}/js/highlight.min.js"></script>
    <script defer src="${website_address}/js/clipboard.min.js"></script>
    % endif
    % if latex:
    <script defer src="${website_address}/js/katex.min.js"></script>
    % endif
    % if image:
    <script defer src="${website_address}/js/fancybox.umd.js"></script>
    % endif
</%def>

<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <title>${title}${f" - {sub_title}" if sub_title else ""}</title>
        ${make_links(latex_enable, image_enable)}
        ${make_scripts(codeblock_enable, latex_enable, image_enable)}
    </head>
    <body>
        <div id="container">
            ${navbar}
            <div id="main">${main}</div>
            ${footer}
        </div>
    </body>
</html>
