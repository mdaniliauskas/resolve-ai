import { type NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const { messages } = await req.json();

  const lastMessage = messages.findLast(
    (m: { role: string }) => m.role === "user"
  );

  if (!lastMessage) {
    return NextResponse.json({ error: "No user message" }, { status: 400 });
  }

  const backendRes = await fetch(`${BACKEND_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: lastMessage.content }),
  });

  if (!backendRes.ok || !backendRes.body) {
    return NextResponse.json({ error: "Backend error" }, { status: 502 });
  }

  // Forward the SSE stream as-is to the browser
  return new Response(backendRes.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
