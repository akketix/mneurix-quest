export const prerender = false;

import fs from "node:fs";
import path from "node:path";

// Disk-backed waitlist store — survives restarts/redeploys.
// File shape: { emails: string[], ts: string, count: number }
const DATA_DIR = path.join(process.cwd(), "data");
const STORE_PATH = path.join(DATA_DIR, "waitlist.json");

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

		// 3. Already subscribed check (normalized to lowercase)
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
