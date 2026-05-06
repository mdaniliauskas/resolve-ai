export type Article = { number: string; title: string };
export type Precedent = { reference: string; summary: string };
export type Channel = { step: number; name: string; description: string };

export type AssistantData = {
  response: string;
  analysis?: {
    is_cdc_case: boolean;
    articles?: Article[];
    precedents?: Precedent[];
  };
  strategy?: {
    channels?: Channel[];
  };
  sources?: string[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  data?: AssistantData;
};
