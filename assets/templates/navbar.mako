<navbar>
    <h1>${title}</h1>
    ${''.join([
        f'<a class="link-style1" href="{link.href}">{link.name}</a>&nbsp;&nbsp;'
        for link in links
    ])}
</navbar>
