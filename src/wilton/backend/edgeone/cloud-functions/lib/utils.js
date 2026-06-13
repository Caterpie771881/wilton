import { createHash } from "node:crypto";

/**
 * @param {number} num
 * @returns {string}
 */
export function formatNumber(num) {
    const n = 2;
    if (num >= 10000) {
        const w = num / 10000;
        return Math.round(w * 10 ** n) / 10 ** n + "w";
    }
    if (num >= 1000) {
        const k = num / 1000;
        return Math.round(k * 10 ** n) / 10 ** n + "k";
    }
    return String(num);
}

/**
 * @param {string} input
 * @returns {string}
 */
export function md5(input) {
    return createHash("md5").update(input).digest("hex");
}

/**
 * @returns {string}
 */
export function getCurrentDate() {
    const today = new Date();
    const year = today.getUTCFullYear();
    const mouth = String(today.getUTCMonth() + 1).padStart(2, "0");
    const day = String(today.getUTCDay()).padStart(2, "0");
    return `${year}-${mouth}-${day}`;
}
