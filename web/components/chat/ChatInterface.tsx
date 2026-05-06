"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./MessageBubble";
import { ExampleCards } from "./ExampleCards";
import type { AssistantData, ChatMessage } from "@/types/chat";

const EXAMPLES = [
  "Comprei um celular e a tela trincou sozinha com 8 dias de uso. A loja recusa a troca.",
  "Meu nome foi parar no SPC por uma dívida que eu já tinha pago.",
  "A academia não quer cancelar meu contrato mesmo eu estando desempregado.",
  "Recebi um produto completamente diferente do que estava anunciado no site.",
];

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, stage]);

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setStage("Entendendo sua situação...");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMsg] }),
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
          if (!part.startsWith("data: ")) continue;
          const payload = JSON.parse(part.slice(6)) as {
            type: string;
            stage?: string;
            data?: AssistantData;
            message?: string;
          };

          if (payload.type === "stage" && payload.stage) {
            setStage(payload.stage);
          } else if (payload.type === "done" && payload.data) {
            setMessages((prev) => [
              ...prev,
              {
                id: crypto.randomUUID(),
                role: "assistant",
                content: payload.data!.response,
                data: payload.data,
              },
            ]);
            setStage("");
            setIsLoading(false);
          } else if (payload.type === "error") {
            setMessages((prev) => [
              ...prev,
              {
                id: crypto.randomUUID(),
                role: "assistant",
                content:
                  payload.message ??
                  "Opa, algo deu errado. Tenta de novo em instantes! 🙏",
              },
            ]);
            setStage("");
            setIsLoading(false);
          }
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "Opa, tive um problema técnico. Tenta de novo em instantes! 🙏",
        },
      ]);
      setStage("");
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full min-h-0 flex-1">
      {/* Messages */}
      <ScrollArea className="flex-1 px-4">
        {isEmpty && !isLoading ? (
          <div className="py-8">
            <p className="text-center text-muted-foreground text-sm mb-6">
              Escolha um exemplo ou descreva sua situação abaixo 👇
            </p>
            <ExampleCards examples={EXAMPLES} onSelect={sendMessage} />
          </div>
        ) : (
          <div className="py-4 space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {isLoading && stage && (
              <div className="flex items-center gap-2 pl-1">
                <span className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-bounce"
                      style={{ animationDelay: `${i * 150}ms` }}
                    />
                  ))}
                </span>
                <span className="text-sm text-muted-foreground animate-pulse">
                  {stage}
                </span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <div className="border-t p-4 bg-background">
        <div className="flex gap-2 items-end max-w-2xl mx-auto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Descreva o que aconteceu com você..."
            className="resize-none min-h-[52px] max-h-32"
            rows={2}
            disabled={isLoading}
          />
          <Button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || isLoading}
            className="h-[52px] px-5 bg-emerald-700 hover:bg-emerald-800 text-white"
          >
            {isLoading ? "..." : "Enviar"}
          </Button>
        </div>
        <p className="text-center text-xs text-muted-foreground mt-2">
          Enter para enviar · Shift+Enter para nova linha
        </p>
      </div>
    </div>
  );
}
