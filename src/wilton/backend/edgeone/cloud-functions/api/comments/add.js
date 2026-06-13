import { getCurrentDate, md5 } from "../../lib/utils";

export async function onRequest({ request }) {
    if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
    }

    try {
        const date = getCurrentDate();

        const body = await request.json();

        const page = body.page;
        const name = body.name;
        const email = body.email;
        const link = body.link;
        const content = body.content;

        const required = [];
        if (page === undefined) {
            required.push("page");
        }
        if (name === undefined) {
            required.push("name");
        }
        if (content === undefined) {
            required.push("content");
        }
        if (required.length) {
            return new Response(JSON.stringify({ required: required }), {
                status: 400,
                headers: { "Content-Type": "application/json" },
            });
        }

        const current_comment = {
            date: date,
            name: encodeURIComponent(String(name)),
            content: encodeURIComponent(String(content)),
        };
        if (email) {
            current_comment.email = encodeURIComponent(String(email));
        }
        if (link) {
            current_comment.link = encodeURIComponent(String(link));
        }

        const key = md5(page);
        /** @type {any[]} */
        const comment_data = JSON.parse((await comments.get(key)) ?? "[]");

        comment_data.push(current_comment);
        await comments.put(key, JSON.stringify(comment_data));

        return new Response(JSON.stringify(current_comment), {
            headers: { "Content-Type": "application/json" },
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
