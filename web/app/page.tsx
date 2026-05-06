import { ChatInterface } from "@/components/chat/ChatInterface";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-emerald-900 to-teal-700 text-white px-4 py-5">
        <div className="max-w-3xl mx-auto flex items-center gap-4">
          <span className="text-3xl">🛡️</span>
          <div>
            <h1 className="text-xl font-extrabold leading-tight tracking-tight">
              Resolve Aí
            </h1>
            <p className="text-sm text-emerald-100 leading-snug">
              Seu direito, explicado de forma simples — de graça e do seu lado.
            </p>
          </div>
        </div>
      </header>

      {/* Disclaimer */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5">
        <p className="max-w-3xl mx-auto text-xs text-amber-800 leading-relaxed">
          ⚠️ <strong>Aviso:</strong> O Resolve Aí orienta com base no CDC (Lei
          8.078/1990) e <strong>não substitui um advogado</strong>. Para casos
          graves, procure o PROCON da sua cidade — é gratuito.
        </p>
      </div>

      {/* Chat */}
      <main className="flex-1 flex flex-col max-w-3xl w-full mx-auto">
        <ChatInterface />
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-muted-foreground py-3 border-t">
        Resolve Aí · Lei 8.078/1990 (CDC) · 🇧🇷
      </footer>
    </div>
  );
}
