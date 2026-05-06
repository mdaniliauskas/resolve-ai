"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./MessageBubble";
import { ExampleCards } from "./ExampleCards";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: AssistantData;
};

type AssistantData = {
  response: string;
  analysis?: {
    is_cdc_case: boolean;
    articles?: { number: string; title: string }[];
    precedents?: { reference: string; summary: string }[];
  };
  strategy?: {
    channels?: { name: string; priority: number; description: string }[];
  };
};

const EXAMPLES = [
  "Comprei um celular e a tela trincou sozinha com 8 dias de uso. A loja recusa a troca.",
  "Meu nome foi parar no SPC por uma dívida que eu já tinha pago.",
  "A academia não quer cancelar meu contrato mesmo eu estando desempregado.",
  "Recebi um produto completamente diferente do que estava anunciado no site.",
];

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMsg] }),
      });

      const data: AssistantData = await res.json();

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
        data,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            "Opa, tive um problema técnico aqui. Tenta de novo em instantes! 🙏",
        },
      ]);
    } finally {
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
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <ScrollArea className="flex-1 px-4">
        {isEmpty ? (
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
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground pl-2">
                <span className="animate-pulse">
                  Estou consultando o Código de Defesa do Consumidor...
                </span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input area */}
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
            Enviar
          </Button>
        </div>
        <p className="text-center text-xs text-muted-foreground mt-2">
          Enter para enviar · Shift+Enter para nova linha
        </p>
      </div>
    </div>
  );
}
