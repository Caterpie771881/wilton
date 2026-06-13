<div>
    <h2>文章类别</h2>
    <ul>
        % for cateory in categories:
        <li>
            <a
                style="color: var(--wilton-color-white)"
                href="${website_address}${cateory.link}"
            >${cateory.name}</a>
            <span class="cateory-num">${len(cateory.posts)}</span>
        </li>
        % endfor
    </ul>
</div>
