import { motion } from "framer-motion";
import { MapPin, Phone, AlertCircle, Star } from "lucide-react";

function ScoreBar({ label, score, color, delay = 0 }) {
  return (
    <div className="flex items-center gap-2 text-[10px]">
      <span className="w-16 text-gray-400">{label}</span>
      <div className="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.6, ease: "easeOut", delay }}
        />
      </div>
      <span className="w-6 text-right text-gray-400">{score}</span>
    </div>
  );
}

function buildWhatsAppLink(provider) {
  const lines = [provider.name || "Doctor"];
  if (provider.specialty) lines.push(provider.specialty);
  if (provider.address) lines.push(provider.address);
  if (provider.phone) lines.push(`Phone: ${provider.phone}`);
  lines.push("");
  if (provider.latitude && provider.longitude) {
    lines.push(`Map: https://maps.google.com/?q=${provider.latitude},${provider.longitude}`);
  } else if (provider.address) {
    lines.push(`Map: https://maps.google.com/maps?q=${encodeURIComponent(provider.address)}`);
  }
  lines.push("");
  lines.push("Found via Sakhi Health Navigator");
  return `https://wa.me/?text=${encodeURIComponent(lines.join("\n"))}`;
}

export default function ProviderCard({ provider, rank, onClick }) {
  const { name, total_score, factors, unverified_factors, address, phone, specialty, rating, reviews_count } = provider;

  return (
    <motion.div
      className="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg hover:shadow-violet-100/50 hover:border-violet-200 transition-all duration-300 cursor-pointer"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.08 }}
      onClick={onClick}
    >
      <div className="p-4">
        {/* header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center shrink-0 shadow-sm">
              <span className="text-[10px] font-bold text-white">#{rank + 1}</span>
            </div>
            <div className="min-w-0">
              <h4 className="font-semibold text-gray-900 text-sm truncate">{name}</h4>
              {specialty && <p className="text-[11px] text-gray-400 truncate">{specialty}</p>}
            </div>
          </div>
          <div className="text-right shrink-0 ml-2">
            <span className="text-lg font-bold bg-gradient-to-r from-violet-600 to-pink-500 bg-clip-text text-transparent">
              {total_score.toFixed(1)}
            </span>
            <p className="text-[9px] text-gray-400 uppercase tracking-wider">score</p>
          </div>
        </div>

        {/* rating */}
        {rating && (
          <div className="flex items-center gap-1.5 mb-2">
            <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
            <span className="text-xs font-semibold text-amber-700">{rating}</span>
            {reviews_count && <span className="text-[10px] text-gray-400">({reviews_count})</span>}
          </div>
        )}

        {/* contact */}
        {address && (
          <div className="flex items-start gap-1.5 text-[11px] text-gray-500 mb-1">
            <MapPin className="w-3 h-3 shrink-0 mt-0.5 text-gray-300" />
            <span className="line-clamp-2">{address}</span>
          </div>
        )}
        {phone && (
          <div className="flex items-center gap-1.5 text-[11px] text-gray-500 mb-3">
            <Phone className="w-3 h-3 shrink-0 text-gray-300" />
            <span>{phone}</span>
          </div>
        )}

        {/* scores */}
        <div className="space-y-1.5 mb-3">
          <ScoreBar label="Specialty" score={factors.specialty_match || 0} color="bg-violet-500" delay={rank * 0.08 + 0.2} />
          <ScoreBar label="Expertise" score={factors.expertise_match || 0} color="bg-pink-500" delay={rank * 0.08 + 0.25} />
          <ScoreBar label="Insurance" score={factors.insurance_match || 0} color="bg-blue-500" delay={rank * 0.08 + 0.3} />
          <ScoreBar label="Location" score={factors.location || 0} color="bg-emerald-500" delay={rank * 0.08 + 0.35} />
          <ScoreBar label="Availability" score={factors.availability || 0} color="bg-amber-500" delay={rank * 0.08 + 0.4} />
        </div>

        {/* unverified */}
        {unverified_factors.length > 0 && (
          <div className="flex items-center gap-1.5 text-[10px] text-amber-600 bg-amber-50 px-2.5 py-1.5 rounded-lg mb-3">
            <AlertCircle className="w-3 h-3 shrink-0" />
            <span>Unverified: {unverified_factors.join(", ")}</span>
          </div>
        )}

        {/* whatsapp */}
        {(address || phone) && (
          <a
            href={buildWhatsAppLink(provider)}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center justify-center gap-1.5 w-full py-2 bg-[#25D366] text-white rounded-xl text-xs font-medium hover:bg-[#1da851] transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
            Share on WhatsApp
          </a>
        )}
      </div>
    </motion.div>
  );
}
