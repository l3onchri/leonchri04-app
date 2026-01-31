"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import ReactMarkdown from "react-markdown";

type Step = "idle" | "transcribing" | "transcribed" | "extracting" | "extracted" | "researching" | "researched" | "generating" | "completed" | "error";

interface TranscriptData {
  text: string;
  metadata: { title: string; url: string };
}

export default function Home() {
  const [url, setUrl] = useState("");
  const [currentStep, setCurrentStep] = useState<Step>("idle");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data from each step
  const [transcript, setTranscript] = useState<TranscriptData | null>(null);
  const [topics, setTopics] = useState<string[]>([]);
  const [research, setResearch] = useState<string>("");
  const [finalScript, setFinalScript] = useState<string>("");

  const resetAll = () => {
    setCurrentStep("idle");
    setTranscript(null);
    setTopics([]);
    setResearch("");
    setFinalScript("");
    setError(null);
  };

  // Step 1: Transcribe
  const handleTranscribe = async () => {
    if (!url) return;

    // Validate YouTube URL
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
    if (!youtubeRegex.test(url)) {
      setError("Inserisci un URL YouTube valido (es. https://youtube.com/watch?v=...)");
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep("transcribing");

    // Sanitize API URL: remove quotes, trailing slashes, and fix common typos (https:77 -> https://)
    let apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    // Remove all whitespace and non-printable characters
    apiUrl = apiUrl.replace(/[\s\n\r"']+/g, '').replace(/\/$/, '');
    // Fix: User likely typed 'https:77' (missing Shift+7 for / on IT layout)
    apiUrl = apiUrl.replace('https:77', 'https://').replace('http:77', 'http://');

    try {
      console.log("Calling transcribe API at:", apiUrl, "for URL:", url);
      const res = await fetch(`${apiUrl}/api/step/transcribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      console.log("Response status:", res.status);
      const data = await res.json();
      console.log("Response data:", data);

      if (data.success) {
        setTranscript(data.data);
        setCurrentStep("transcribed");
      } else {
        setError(data.error || "Errore sconosciuto dal server");
        setCurrentStep("error");
      }
    } catch (e: any) {
      console.error("Fetch error:", e);
      setError(`Errore di connessione (${apiUrl}): ${e.message || e}`);
      setCurrentStep("error");
    }
    setLoading(false);
  };

  // Step 2: Extract Topics
  const handleExtractTopics = async () => {
    if (!transcript) return;
    setLoading(true);
    setError(null);
    setCurrentStep("extracting");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/step/extract-topics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript_text: transcript.text }),
      });
      const data = await res.json();

      if (data.success) {
        setTopics(data.data);
        setCurrentStep("extracted");
      } else {
        setError(data.error);
        setCurrentStep("error");
      }
    } catch (e) {
      setError("Errore di connessione al backend");
      setCurrentStep("error");
    }
    setLoading(false);
  };

  // Step 3: Research
  const handleResearch = async () => {
    if (topics.length === 0) return;
    setLoading(true);
    setError(null);
    setCurrentStep("researching");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/step/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topics }),
      });
      const data = await res.json();

      if (data.success) {
        setResearch(data.data);
        setCurrentStep("researched");
      } else {
        setError(data.error);
        setCurrentStep("error");
      }
    } catch (e) {
      setError("Errore di connessione al backend");
      setCurrentStep("error");
    }
    setLoading(false);
  };

  // Step 4: Generate Script
  const handleGenerateScript = async () => {
    if (!transcript || !research) return;
    setLoading(true);
    setError(null);
    setCurrentStep("generating");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/step/generate-script`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript_text: transcript.text, research }),
      });
      const data = await res.json();

      if (data.success) {
        setFinalScript(data.data);
        setCurrentStep("completed");
      } else {
        setError(data.error);
        setCurrentStep("error");
      }
    } catch (e) {
      setError("Errore di connessione al backend");
      setCurrentStep("error");
    }
    setLoading(false);
  };

  const isStepDone = (step: string) => {
    const order = ["transcribed", "extracted", "researched", "completed"];
    const currentIdx = order.indexOf(currentStep);
    const stepIdx = order.indexOf(step);
    return currentIdx >= stepIdx && stepIdx !== -1;
  };

  return (
    <main className="min-h-screen p-16 max-w-7xl mx-auto flex flex-col gap-12">
      {/* Header */}
      <header className="text-center space-y-4">
        <h1 className="text-6xl font-bold tracking-tighter text-white">
          LEONCHRI04 <span className="text-brand-yellow">GENERATOR</span>
        </h1>
        <p className="text-gray-400 text-2xl">
          Trasforma video YouTube in script virali con l'AI.
        </p>
      </header>

      {/* Input Section */}
      <section className="bg-surface p-12 rounded-2xl border border-gray-800 shadow-2xl space-y-10">
        <div className="flex gap-4 items-end">
          <Input
            label="URL Video YouTube"
            placeholder="https://youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={currentStep !== "idle"}
          />
          {currentStep === "idle" ? (
            <Button onClick={handleTranscribe} isLoading={loading} disabled={loading || !url}>
              Avvia
            </Button>
          ) : (
            <Button variant="secondary" onClick={resetAll}>
              Ricomincia
            </Button>
          )}
        </div>

        {/* Progress Steps */}
        <div className="grid grid-cols-4 gap-6 text-center text-base pt-8 border-t border-gray-800">
          <StepIndicator label="1. Trascrivi" active={currentStep === "transcribing"} done={isStepDone("transcribed")} />
          <StepIndicator label="2. Argomenti" active={currentStep === "extracting"} done={isStepDone("extracted")} />
          <StepIndicator label="3. Ricerca" active={currentStep === "researching"} done={isStepDone("researched")} />
          <StepIndicator label="4. Genera" active={currentStep === "generating"} done={isStepDone("completed")} />
        </div>

        {error && (
          <div className="p-4 bg-red-900/20 border border-red-500/50 text-red-200 rounded-lg">
            Errore: {error}
          </div>
        )}
      </section>

      {/* Step 1 Result: Transcript */}
      {transcript && currentStep !== "idle" && (
        <section className="bg-surface p-6 rounded-2xl border border-gray-800 space-y-4 animate-in fade-in slide-in-from-bottom duration-500">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-brand-yellow">📝 Trascrizione</h2>
            {transcript.metadata.title && (
              <span className="text-gray-400 text-sm">{transcript.metadata.title}</span>
            )}
          </div>
          <div className="bg-black/50 p-4 rounded-lg max-h-64 overflow-y-auto text-gray-300 text-sm leading-relaxed">
            {transcript.text.substring(0, 2000)}
            {transcript.text.length > 2000 && "..."}
          </div>
          <div className="text-gray-500 text-sm">
            {transcript.text.length} caratteri totali
          </div>

          {currentStep === "transcribed" && (
            <Button onClick={handleExtractTopics} isLoading={loading} className="w-full">
              ➡️ Continua: Estrai Topics
            </Button>
          )}
        </section>
      )}

      {/* Step 2 Result: Topics */}
      {topics.length > 0 && (
        <section className="bg-surface p-6 rounded-2xl border border-gray-800 space-y-4 animate-in fade-in slide-in-from-bottom duration-500">
          <h2 className="text-2xl font-bold text-brand-yellow">🎯 Topics Estratti</h2>
          <div className="flex flex-wrap gap-2">
            {topics.map((topic, i) => (
              <span key={i} className="bg-brand-yellow/10 border border-brand-yellow/30 text-brand-yellow px-4 py-2 rounded-full text-sm">
                {topic}
              </span>
            ))}
          </div>

          {currentStep === "extracted" && (
            <Button onClick={handleResearch} isLoading={loading} className="w-full">
              ➡️ Continua: Ricerca Online
            </Button>
          )}
        </section>
      )}

      {/* Step 3 Result: Research */}
      {research && (
        <section className="bg-surface p-6 rounded-2xl border border-gray-800 space-y-4 animate-in fade-in slide-in-from-bottom duration-500">
          <h2 className="text-2xl font-bold text-brand-yellow">🔍 Ricerca</h2>
          <div className="bg-black/50 p-4 rounded-lg max-h-96 overflow-y-auto prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{research.substring(0, 5000)}</ReactMarkdown>
          </div>

          {currentStep === "researched" && (
            <Button onClick={handleGenerateScript} isLoading={loading} className="w-full">
              ➡️ Continua: Genera Script
            </Button>
          )}
        </section>
      )}

      {/* Step 4 Result: Final Script */}
      {finalScript && (
        <section className="bg-surface p-6 rounded-2xl border border-brand-yellow/50 space-y-4 animate-in fade-in slide-in-from-bottom duration-500">
          <div className="flex justify-between items-center">
            <h2 className="text-3xl font-bold text-brand-yellow">✨ Script Generato</h2>
            <Button variant="secondary" onClick={() => navigator.clipboard.writeText(finalScript)}>
              📋 Copia
            </Button>
          </div>
          <div className="bg-black/50 p-6 rounded-lg prose prose-invert prose-yellow max-w-none">
            <ReactMarkdown>{finalScript}</ReactMarkdown>
          </div>
        </section>
      )}
    </main>
  );
}

function StepIndicator({ label, active, done }: { label: string, active: boolean, done: boolean }) {
  return (
    <div className={`p-4 rounded-lg border text-lg transition-all duration-300 ${active ? "bg-brand-yellow/10 border-brand-yellow text-brand-yellow font-bold animate-pulse" :
      done ? "bg-green-900/10 border-green-500/30 text-green-500" :
        "bg-black border-gray-800 text-gray-600"
      }`}>
      {label}
    </div>
  );
}
