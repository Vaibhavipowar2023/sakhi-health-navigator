import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, Heart, X } from "lucide-react";
import ChatWindow from "../components/ChatWindow";
import ProviderCard from "../components/ProviderCard";
import ProviderModal from "../components/ProviderModal";
import CrisisBanner from "../components/CrisisBanner";
import LanguageToggle from "../components/LanguageToggle";
import LocationDetector from "../components/LocationDetector";
import { sendChat } from "../api";

const LANG_INSTRUCTIONS = {
  en: "",
  hi: "\n[Respond in Hindi]",
  mr: "\n[Respond in Marathi]",
};

export default function ChatApp() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [crisis, setCrisis] = useState(false);
  const [providers, setProviders] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [selectedRank, setSelectedRank] = useState(0);
  const [language, setLanguage] = useState(() => {
    try { return localStorage.getItem("sakhi_lang") || "en"; } catch { return "en"; }
  });
  const [detectedCity, setDetectedCity] = useState("");

  useEffect(() => {
    try { localStorage.setItem("sakhi_lang", language); } catch {}
  }, [language]);

  const buildConversation = (allMessages) => {
    return allMessages
      .map((m) => (m.role === "user" ? `Patient: ${m.text}` : `Sakhi: ${m.text}`))
      .join("\n");
  };

  const handleSend = async (text) => {
    const updatedMessages = [...messages, { role: "user", text }];
    setMessages(updatedMessages);
    setLoading(true);

    try {
      let conversation = buildConversation(updatedMessages);

      if (detectedCity && messages.length === 0) {
        conversation = `[Patient is located in ${detectedCity}]\n` + conversation;
      }
      conversation += LANG_INSTRUCTIONS[language] || "";

      const data = await sendChat(conversation, sessionId);
      setSessionId(data.session_id);

      if (data.crisis) setCrisis(true);

      if (data.ranked_providers?.length > 0) {
        setProviders(data.ranked_providers);
        setShowResults(true);
      } else if (data.needs_more_info) {
        setShowResults(false);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply, whatsapp_link: data.whatsapp_link || "" },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* chat panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* header */}
        <header className="relative bg-white border-b border-gray-100 z-20">
          <div className="flex items-center gap-3 px-4 py-3">
            <button
              onClick={() => navigate("/")}
              className="p-1.5 text-gray-400 hover:text-violet-600 rounded-lg hover:bg-violet-50 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shadow-sm">
              <Heart className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-sm font-semibold text-gray-900">Sakhi</h1>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                <p className="text-[11px] text-gray-400">Online</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <LocationDetector city={detectedCity} onCityDetected={setDetectedCity} />
              <LanguageToggle language={language} onLanguageChange={setLanguage} />
            </div>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-violet-500 via-pink-500 to-violet-500 opacity-50" />
        </header>

        <AnimatePresence>{crisis && <CrisisBanner />}</AnimatePresence>

        <ChatWindow messages={messages} onSend={handleSend} loading={loading} language={language} />
      </div>

      {/* desktop results panel */}
      <AnimatePresence>
        {showResults && (
          <motion.aside
            className="w-96 border-l border-gray-100 bg-white overflow-y-auto hidden lg:block"
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 100, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
          >
            <div className="sticky top-0 z-10 bg-gradient-to-r from-violet-50 to-pink-50 border-b border-gray-100 p-4">
              <h2 className="font-semibold text-gray-900">Recommended Specialists</h2>
              <p className="text-xs text-gray-500 mt-1">Ranked by selected criteria</p>
            </div>
            <div className="p-4 space-y-3">
              {providers.map((p, i) => (
                <ProviderCard
                  key={p.provider_id}
                  provider={p}
                  rank={i}
                  onClick={() => { setSelectedProvider(p); setSelectedRank(i); }}
                />
              ))}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* mobile bottom sheet */}
      <AnimatePresence>
        {showResults && (
          <motion.div
            className="fixed inset-x-0 bottom-0 bg-white rounded-t-2xl shadow-2xl border-t border-gray-200 max-h-[60vh] overflow-y-auto lg:hidden z-40"
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
          >
            <div className="sticky top-0 bg-white p-4 border-b border-gray-100 flex items-center justify-between z-10">
              <div>
                <h2 className="font-semibold text-gray-900">Recommended Specialists</h2>
                <p className="text-xs text-gray-500">Ranked by selected criteria</p>
              </div>
              <button
                onClick={() => setShowResults(false)}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 space-y-3">
              {providers.map((p, i) => (
                <ProviderCard
                  key={p.provider_id}
                  provider={p}
                  rank={i}
                  onClick={() => { setSelectedProvider(p); setSelectedRank(i); }}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {selectedProvider && (
          <ProviderModal
            provider={selectedProvider}
            rank={selectedRank}
            onClose={() => setSelectedProvider(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
