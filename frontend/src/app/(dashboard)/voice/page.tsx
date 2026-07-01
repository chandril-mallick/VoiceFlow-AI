"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Settings2, Globe2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth";

export default function VoiceAgentPage() {
  const { tenant } = useAuth();
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState<{ role: string; content: string; language?: string }[]>([]);
  const [currentStage, setCurrentStage] = useState("greeting");
  const [language, setLanguage] = useState("en");
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Fallback testing config
  const startConversation = () => {
    setTranscript([]);
    setIsRecording(true);

    const token = localStorage.getItem("vf_access_token");
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/voice?token=${token}`;
    
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      wsRef.current?.send(
        JSON.stringify({
          type: "start",
          config: {
            company_name: tenant?.name || "Our Company",
            services: ["Software Development", "AI Consulting"],
            language: language,
          },
        })
      );
      startAudioCapture();
    };

    wsRef.current.onmessage = async (event) => {
      if (typeof event.data === "string") {
        const data = JSON.parse(event.data);
        if (data.type === "greeting" || data.type === "response") {
          setTranscript((prev) => [
            ...prev,
            ...(data.user_text ? [{ role: "user", content: data.user_text, language: data.language }] : []),
            { role: "assistant", content: data.text, language: data.language },
          ]);
          setCurrentStage(data.stage);
          if (data.is_ended) stopConversation();
        }
      } else if (event.data instanceof Blob) {
        // Play received audio
        const audioUrl = URL.createObjectURL(event.data);
        const audio = new Audio(audioUrl);
        await audio.play();
      }
    };
  };

  const startAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: "audio/webm" });

      mediaRecorderRef.current.ondataavailable = async (e) => {
        if (e.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // In a real app, you'd convert WebM to raw PCM here before sending
          // For now, we simulate sending chunks
          wsRef.current.send(e.data);
        }
      };

      mediaRecorderRef.current.start(250); // Send every 250ms
    } catch (err) {
      console.error("Microphone access denied:", err);
      stopConversation();
    }
  };

  const stopConversation = () => {
    setIsRecording(false);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
    }
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "stop" }));
      setTimeout(() => wsRef.current?.close(), 1000);
    }
  };

  // Mock text input for testing without microphone
  const [textInput, setTextInput] = useState("");
  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({ type: "text_input", text: textInput }));
    setTextInput("");
  };

  return (
    <div className="p-8 h-full flex flex-col max-w-5xl mx-auto">
      <div className="flex flex-col items-center justify-center mb-8">
        <h1 className="text-3xl font-bold font-[family-name:var(--font-outfit)] gradient-text mb-2">
          Test Your AI Sales Agent
        </h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Have a real-time voice conversation with your AI representative.
        </p>
      </div>

      <div className="flex-1 glass rounded-3xl p-6 flex flex-col overflow-hidden relative">
        {/* Controls */}
        <div className="absolute top-6 left-6 right-6 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))] flex items-center gap-2 text-sm font-medium">
              <Settings2 className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              Stage: <span className="text-[hsl(var(--primary))] capitalize">{currentStage.replace("_", " ")}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-xl p-1">
            {["en", "hi", "bn"].map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                disabled={isRecording}
                className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  language === lang
                    ? "bg-[hsl(var(--primary))] text-white"
                    : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
                }`}
              >
                {lang === "en" ? "EN" : lang === "hi" ? "HI" : "BN"}
              </button>
            ))}
          </div>
        </div>

        {/* Transcript Area */}
        <div className="flex-1 overflow-y-auto pt-16 pb-32 px-4 space-y-6">
          {transcript.length === 0 && !isRecording && (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-50">
              <Mic className="w-16 h-16 mb-4" />
              <p>Click the microphone to start a conversation</p>
            </div>
          )}
          
          <AnimatePresence>
            {transcript.map((msg, i) => (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                key={i}
                className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[80%] px-6 py-4 rounded-2xl ${
                    msg.role === "user"
                      ? "bg-[hsl(var(--primary))] text-white rounded-br-sm"
                      : "bg-[hsl(var(--muted)/0.5)] border border-[hsl(var(--border))] rounded-bl-sm"
                  }`}
                >
                  <p className="text-lg leading-relaxed">{msg.content}</p>
                </div>
                {msg.language && (
                  <span className="text-xs text-[hsl(var(--muted-foreground))] mt-2 flex items-center gap-1">
                    <Globe2 className="w-3 h-3" />
                    {msg.language.toUpperCase()}
                  </span>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Mic Button Area */}
        <div className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-[hsl(var(--card))] via-[hsl(var(--card)/0.9)] to-transparent flex flex-col items-center justify-center">
          <div className="relative">
            {isRecording && (
              <motion.div
                className="absolute inset-0 rounded-full bg-[hsl(var(--primary)/0.2)] pulse-ring"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              />
            )}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={isRecording ? stopConversation : startConversation}
              className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center shadow-xl transition-colors ${
                isRecording
                  ? "bg-gradient-to-br from-[hsl(var(--destructive))] to-red-600 glow-secondary"
                  : "bg-gradient-to-br from-[hsl(var(--primary))] to-[hsl(var(--secondary))] glow-primary"
              }`}
            >
              {isRecording ? <MicOff className="w-8 h-8 text-white" /> : <Mic className="w-8 h-8 text-white" />}
            </motion.button>
          </div>
          
          {/* Text fallback for testing */}
          {isRecording && (
            <form onSubmit={handleTextSubmit} className="mt-6 w-full max-w-md flex gap-2">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Type a message to simulate voice..."
                className="flex-1 px-4 py-2 rounded-xl bg-[hsl(var(--muted))] border border-[hsl(var(--border))] text-sm focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
              <button type="submit" className="px-4 py-2 rounded-xl bg-[hsl(var(--primary))] text-white text-sm font-medium">
                Send
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
