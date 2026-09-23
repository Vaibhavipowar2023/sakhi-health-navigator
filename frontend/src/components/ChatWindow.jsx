import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader2 } from "lucide-react";

function SakhiAvatar({ size = "sm" }) {
  const px = size === "lg" ? "w-10 h-10" : "w-7 h-7";
  const svg = size === "lg" ? "w-5 h-5" : "w-3.5 h-3.5";
  return (
    <div className={`${px} rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shrink-0 shadow-sm`}>
      <svg viewBox="0 0 120 120" className={svg}>
        <circle cx="60" cy="38" r="9" fill="white" />
        <path d="M60 47 C60 47,47 56,45 74 C44 82,52 85,60 85 C68 85,76 82,75 74 C73 56,60 47,60 47Z" fill="white" opacity="0.9" />
        <path d="M55 66 C55 63.5,52.5 62,50.5 62 C48 62,46 64,46 66 C46 69,55 74,55 74 C55 74,64 69,64 66 C64 64,62 62,59.5 62 C57.5 62,55 63.5,55 66Z" fill="#F472B6" opacity="0.8" />
      </svg>
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      className={`flex gap-2.5 ${isUser ? "justify-end" : "justify-start"}`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      {!isUser && <SakhiAvatar />}

      <div className={`max-w-[75%] ${isUser ? "" : ""}`}>
        <div
          className={`px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-gradient-to-r from-violet-600 to-violet-500 text-white rounded-2xl rounded-br-md shadow-sm shadow-violet-200/50"
              : "bg-white text-gray-800 rounded-2xl rounded-bl-md shadow-sm border border-gray-100"
          }`}
        >
          {message.text}
        </div>
        {message.whatsapp_link && (
          <a
            href={message.whatsapp_link}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-[#25D366] text-white rounded-xl text-sm font-medium hover:bg-[#1da851] transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
            Share on WhatsApp
          </a>
        )}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <motion.div className="flex gap-2.5 justify-start" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <SakhiAvatar />
      <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-1.5 h-1.5 bg-violet-400 rounded-full"
              animate={{ y: [0, -5, 0] }}
              transition={{ duration: 0.5, delay: i * 0.12, repeat: Infinity }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}

const PLACEHOLDERS = {
  en: "Describe how you're feeling...",
  hi: "बताइए आपको क्या तकलीफ है...",
  mr: "तुम्हाला काय त्रास होतोय ते सांगा...",
};

export default function ChatWindow({ onSend, messages, loading, language = "en" }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;
    onSend(text);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-gray-50/50">
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
              className="max-w-sm"
            >
              <SakhiAvatar size="lg" />
              <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2">Hi, I'm Sakhi</h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                Tell me what's going on and I'll find the right doctor near you. Everything stays private.
              </p>
              <div className="mt-6 flex flex-wrap gap-2 justify-center">
                {[
                  "I've been having irregular periods",
                  "My knee has been hurting for weeks",
                  "I need a skin specialist in Pune",
                  "I'm feeling very anxious lately",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => { setInput(suggestion); inputRef.current?.focus(); }}
                    className="px-3.5 py-2 text-xs text-violet-700 bg-white border border-violet-100 rounded-full hover:bg-violet-50 hover:border-violet-200 transition-all shadow-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </motion.div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, i) => <MessageBubble key={i} message={msg} />)}
        </AnimatePresence>

        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 px-4 py-3 bg-white">
        <div className="flex items-center gap-2 max-w-3xl mx-auto">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={PLACEHOLDERS[language] || PLACEHOLDERS.en}
            className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-full text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition-all placeholder:text-gray-400"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2.5 bg-gradient-to-r from-violet-600 to-pink-500 text-white rounded-full disabled:opacity-40 hover:shadow-md hover:shadow-violet-200 transition-all duration-200"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
      </form>
    </div>
  );
}
