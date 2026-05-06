"use client";

type Props = {
  examples: string[];
  onSelect: (text: string) => void;
};

export function ExampleCards({ examples, onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
      {examples.map((example) => (
        <button
          key={example}
          onClick={() => onSelect(example)}
          className="text-left rounded-xl border border-border bg-card hover:border-emerald-400 hover:bg-emerald-50/50 transition-colors p-4 text-sm text-muted-foreground hover:text-foreground cursor-pointer"
        >
          {example}
        </button>
      ))}
    </div>
  );
}
