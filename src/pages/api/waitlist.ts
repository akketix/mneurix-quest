export const prerender = false;

import fs from "node:fs";
import path from "node:path";

// Disk-backed waitlist store — survives restarts/redeploys.
// File shape: { emails: string[], ts: string, count: number }
// On DO App Platform, set MNEURIX_QUEST_DATA_DIR to a persistent-volume mount
// (e.g. /data) so signups survive redeploys; defaults to ./data locally.
const DATA_DIR = process.env.MNEURIX_QUEST_DATA_DIR
	? path.resolve(process.env.MNEURIX_QUEST_DATA_DIR)
	: path.join(process.cwd(), "data");
const STORE_PATH = path.join(DATA_DIR, "waitlist.json");

// Per-IP rate limiting (matches mneurix.dev): 3 signups per 10 min. In-memory;
// resets on redeploy, which is fine — it only exists to stop rotating-IP bots
// from flooding the list, not as a durable quota.
const RATE_WINDOW_MS = 10 * 60 * 1000; // 10 min
const RATE_MAX = 3;
const hits = new Map<string, number[]>();

function clientIp(req: Request): string {
	const fwd = req.headers.get("x-forwarded-for");
	if (fwd) return fwd.split(",")[0]!.trim();
	return "unknown";
}

function rateLimited(ip: string): boolean {
	const now = Date.now();
	const arr = (hits.get(ip) ?? []).filter((t) => now - t < RATE_WINDOW_MS);
	arr.push(now);
	hits.set(ip, arr);
	return arr.length > RATE_MAX;
}

function readSubs(): string[] {
	try {
		const raw = fs.readFileSync(STORE_PATH, "utf8");
		const parsed = JSON.parse(raw);
		if (parsed && Array.isArray(parsed.emails)) {
			return parsed.emails.filter((e: unknown) => typeof e === "string");
		}
		return [];
	} catch {
		// Missing or corrupt file — start empty.
		return [];
	}
}

function writeSubs(list: string[]): void {
	fs.mkdirSync(DATA_DIR, { recursive: true });
	// Atomic write: temp file in the SAME directory, then rename.
	const tmpPath = path.join(DATA_DIR, `waitlist.json.${process.pid}.tmp`);
	const payload = {
		emails: list,
		ts: new Date().toISOString(),
		count: list.length,
	};
	fs.writeFileSync(tmpPath, JSON.stringify(payload, null, 2), "utf8");
	fs.renameSync(tmpPath, STORE_PATH);
}

export async function POST({ request }: { request: Request }) {
	try {
		const data = await request.json();
		const email = (data.email || "").trim().toLowerCase();
		const company = (data.company || "").trim(); // Honeypot field

		// 1. Bot Honeypot Check (bots fill out hidden fields, real users do not)
		if (company) {
			return new Response(JSON.stringify({ ok: true, msg: "Subscribed" }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		}

		// 2. Email Validation
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!email || !emailRegex.test(email)) {
			return new Response(
				JSON.stringify({ ok: false, error: "invalid_email" }),
				{
					status: 400,
					headers: { "Content-Type": "application/json" },
				},
			);
		}

		// 3. Rate limit (per-IP, 3 per 10 min) — matches mneurix.dev
		if (rateLimited(clientIp(request))) {
			return new Response(JSON.stringify({ ok: false, error: "rate_limited" }), {
				status: 429,
				headers: { "Content-Type": "application/json" },
			});
		}

		// 4. Already subscribed check (normalized to lowercase)
		const subs = readSubs();
		if (subs.includes(email)) {
			return new Response(JSON.stringify({ ok: true, already: true }), {
				status: 200,
				headers: { "Content-Type": "application/json" },
			});
		}

		subs.push(email);
		writeSubs(subs);

		return new Response(JSON.stringify({ ok: true, already: false }), {
			status: 200,
			headers: { "Content-Type": "application/json" },
		});
	} catch (err) {
		return new Response(JSON.stringify({ ok: false, error: "server_error" }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}
