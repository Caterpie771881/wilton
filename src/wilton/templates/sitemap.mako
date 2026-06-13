<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>${website_address}/index.html</loc>
        <priority>1</priority>
    </url>
    <url>
        <loc>${website_address}/friends.html</loc>
        <priority>0</priority>
    </url>
    % for post in posts:
    <url>
        <loc>${website_address}${post.link}</loc>
        <priority>0.5</priority>
    </url>
    % endfor
    % for page in pages:
    <url>
        <loc>${website_address}${page.link}</loc>
        <priority>0.6</priority>
    </url>
    % endfor
</urlset>
