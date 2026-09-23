import { useState, useRef, useEffect } from "react";
import { Globe } from "lucide-react";

const LANGUAGES = [
  { code: "en", label: "English", short: "EN" },
  { code: "hi", label: "हिंदी", short: "हिं" },
  { code: "mr", label: "मराठी", short: "मरा" },
];

export default function LanguageToggle({ language, onLanguageChange }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const current = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Globe className="w-3.5 h-3.5" />
        <span>{current.short}</span>
      </button>

      {open && (
        <div className="absolute right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-20 min-w-[120px]">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                onLanguageChange(lang.code);
                setOpen(false);
              }}
              className={`w-full text-left px-3 py-1.5 text-sm hover:bg-violet-50 transition-colors ${
                lang.code === language
                  ? "text-violet-600 font-medium bg-violet-50"
                  : "text-gray-700"
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
