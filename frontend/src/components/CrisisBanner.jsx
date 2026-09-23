import { motion } from "framer-motion";
import { AlertTriangle, Phone } from "lucide-react";

export default function CrisisBanner() {
  return (
    <motion.div
      className="bg-red-50 border border-red-200 rounded-xl p-4 mx-4 mt-4"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
        <div>
          <p className="font-semibold text-red-800 text-sm">
            Immediate Support Available
          </p>
          <p className="text-red-700 text-sm mt-1">
            If you're in crisis, please reach out for help right now:
          </p>
          <div className="flex flex-wrap gap-3 mt-3">
            <a
              href="tel:112"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-xs font-medium hover:bg-red-200 transition-colors"
            >
              <Phone className="w-3 h-3" /> Emergency: 112
            </a>
            <a
              href="tel:9152987821"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-xs font-medium hover:bg-red-200 transition-colors"
            >
              <Phone className="w-3 h-3" /> iCall: 9152987821
            </a>
            <a
              href="tel:18005990019"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-xs font-medium hover:bg-red-200 transition-colors"
            >
              <Phone className="w-3 h-3" /> Women Helpline: 1800-599-0019
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
