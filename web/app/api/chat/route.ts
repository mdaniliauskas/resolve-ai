import { type NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const { messages } = await req.json();

  // Send only the last user message to the stateless FastAPI backend
  const lastMessage = messages.findLast(
    (m: { role: string }) => m.role === "user"
  );

  if (!lastMessage) {
    return NextResponse.json({ error: "No user message" }, { status: 400 });
  }

  const backendRes = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: lastMessage.content }),
  });

  if (!backendRes.ok) {
    return NextResponse.json(
      { error: "Backend error" },
      { status: backendRes.status }
    );
  }

  const data = await backendRes.json();
  return NextResponse.json(data);
}
