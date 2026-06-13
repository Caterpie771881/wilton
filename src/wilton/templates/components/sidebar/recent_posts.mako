<div>
    <h2>最近文章</h2>
    <ul>
        % for post in posts:
        <li>
            <a
                style="color: var(--wilton-color-white)"
                href="${website_address}${post.link}"
            >${post.title}</a>
        </li>
        <div class="post-date">${post.date.strftime("%Y-%m-%d")}</div>
        % endfor
    </ul>
</div>
