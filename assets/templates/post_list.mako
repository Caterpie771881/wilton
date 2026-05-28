<%def name="make_pagination(total, current)">
    <div class="pagination">
        <% left = max(1, current-2) %><% right = min(total, left + 3) + 1 %>
        % if left > 1:
        <a href="post_list_1.html">&lt;&lt;</a>
        ...
        % endif
        % for i in range(left, right):
        <a href="post_list_${i}.html" ${'class="current-page"' if current == i else ''}>${i}</a>
        % if i < right - 1:
        |
        % endif
        % endfor
        % if right < total + 1:
        ...
        <a href="post_list_${total}.html">&gt;&gt;</a>
        % endif
    </div>
</%def>

<div id="mainbar">
    <h1>${title}</h1>
    % for post in posts:
    <div class="post-card">
        <a href="${config.website_address}${post.link}"><h2>${post.title}</h2></a>
        <a class="link-style2" href="${post.category.link}">${post.category.name}</a>
        <div>${post.intro}</div>
        <blockquote>
            <p>
                Post on ${post.date.strftime("%Y-%m-%d")} |
                views: <span class="page-view" link="${post.link}">loading...</span> |
                comment: <span class="comment-count" link="${post.link}">loading...</span>
            </p>
        </blockquote>
    </div>
    % endfor
    ${make_pagination(total_pages, current_page)}
</div>

${sidebar}
