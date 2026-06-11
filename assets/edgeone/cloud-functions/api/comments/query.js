import { md5 } from "../../lib/utils";

export async function onRequest({ request }) {
    if (request.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
    }

    try {
        const body = await request.json();
        /** @type {string[]} */
        const pages = body.pages ?? [];

        const results = await Promise.all(
            pages.map(async (page) => {
                const key = md5(page);
                console.log(`key: ${key}`);
                /** @type {string} */
                const comment_data = (await comments.get(key)) ?? "[]";
                console.log("comment_data:");
                console.log(comment_data);
                return { page, comments: JSON.parse(comment_data) };
            }),
        );

        const result = {};
        for (const { page, comments } of results) {
            result[page] = comments;
        }

        return new Response(JSON.stringify(result), {
            headers: { "Content-Type": "application/json" },
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        });
    }
}
