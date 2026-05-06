"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { ChatMessage } from "@/types/chat";

export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-emerald-700 text-white px-4 py-3 text-sm leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  const { data } = message;
  const articles = data?.analysis?.articles ?? [];
  const precedents = data?.analysis?.precedents ?? [];
  const channels = data?.strategy?.channels ?? [];
  const isCdcCase = data?.analysis?.is_cdc_case;

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] space-y-3">
        {/* Main response */}
        <div className="rounded-2xl rounded-tl-sm bg-muted px-4 py-3 text-sm leading-relaxed">
          {isCdcCase !== undefined && (
            <Badge
              variant={isCdcCase ? "default" : "secondary"}
              className={`mb-2 ${isCdcCase ? "bg-emerald-700" : ""}`}
            >
              {isCdcCase ? "✅ CDC se aplica ao seu caso" : "ℹ️ Fora do CDC"}
            </Badge>
          )}
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Artigos do CDC */}
        {articles.length > 0 && (
          <Card className="border-emerald-200 bg-emerald-50/50">
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm text-emerald-800">
                📋 Artigos do CDC que protegem você
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 space-y-1">
              {articles.map((a) => (
                <div key={a.number} className="text-xs text-emerald-900">
                  <span className="font-semibold">{a.number}</span> — {a.title}
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Próximos passos */}
        {channels.length > 0 && (
          <Card className="border-blue-200 bg-blue-50/50">
            <CardHeader className="pb-2 pt-3 px-4">
              <CardTitle className="text-sm text-blue-800">
                🗺️ Por onde começar
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-3 space-y-2">
              {channels
                .sort((a, b) => a.step - b.step)
                .map((ch) => (
                  <div key={ch.name} className="flex gap-2 text-xs text-blue-900">
                    <span className="font-bold shrink-0">{ch.step}.</span>
                    <div>
                      <span className="font-semibold">{ch.name}</span>
                      {ch.description && (
                        <span className="text-blue-700"> — {ch.description}</span>
                      )}
                    </div>
                  </div>
                ))}
            </CardContent>
          </Card>
        )}

        {/* Jurisprudência */}
        {precedents.length > 0 && (
          <>
            <Separator />
            <div className="px-1">
              <p className="text-xs font-semibold text-muted-foreground mb-1">
                ⚖️ Decisões do STJ sobre casos parecidos
              </p>
              {precedents.map((p) => (
                <p key={p.reference} className="text-xs text-muted-foreground">
                  <span className="font-medium">{p.reference}</span>:{" "}
                  {p.summary}
                </p>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
