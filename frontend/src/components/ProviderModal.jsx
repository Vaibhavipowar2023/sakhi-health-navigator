import { motion, AnimatePresence } from "framer-motion";
import { X, MapPin, Phone, Clock, Star, Shield, ExternalLink } from "lucide-react";

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

function buildMapsLink(provider) {
  if (provider.latitude && provider.longitude) {
    return `https://maps.google.com/?q=${provider.latitude},${provider.longitude}`;
  }
  if (provider.address) {
    return `https://maps.google.com/maps?q=${encodeURIComponent(provider.address)}`;
  }
  return null;
}

function formatHours(hours) {
  if (!hours) return null;
  const dayOrder = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
  const shortDay = { monday: "Mon", tuesday: "Tue", wednesday: "Wed", thursday: "Thu", friday: "Fri", saturday: "Sat", sunday: "Sun" };
  return dayOrder
    .filter((d) => hours[d])
    .map((d) => ({ day: shortDay[d], time: hours[d] }));
}

export default function ProviderModal({ provider, rank, onClose }) {
  if (!provider) return null;

  const mapsLink = buildMapsLink(provider);
  const whatsappLink = buildWhatsAppLink(provider);
  const hoursList = formatHours(provider.hours);

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        {/* backdrop */}
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

        {/* modal */}
        <motion.div
          className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
        >
          {/* header */}
          <div className="sticky top-0 bg-white border-b border-gray-100 px-5 py-4 flex items-start justify-between rounded-t-2xl z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold text-violet-600 bg-violet-50 px-2 py-0.5 rounded-full">
                  #{rank + 1}
                </span>
                <h2 className="text-lg font-semibold text-gray-900">{provider.name}</h2>
              </div>
              {provider.specialty && (
                <p className="text-sm text-gray-500">{provider.specialty}</p>
              )}
              {provider.credentials && (
                <p className="text-xs text-gray-400 mt-0.5">{provider.credentials}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="px-5 py-4 space-y-4">
            {/* rating */}
            {provider.rating && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 rounded-lg">
                  <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                  <span className="text-sm font-semibold text-amber-700">{provider.rating}</span>
                </div>
                {provider.reviews_count && (
                  <span className="text-sm text-gray-500">
                    {provider.reviews_count.toLocaleString()} reviews
                  </span>
                )}
              </div>
            )}

            {/* score */}
            <div className="flex items-center gap-2 text-sm">
              <Shield className="w-4 h-4 text-violet-500" />
              <span className="text-gray-600">Match score:</span>
              <span className="font-bold text-violet-600">{provider.total_score.toFixed(1)}</span>
              <span className="text-gray-400">/ 100</span>
            </div>

            {/* contact details */}
            <div className="bg-gray-50 rounded-xl p-4 space-y-3">
              {provider.address && (
                <div className="flex items-start gap-3">
                  <MapPin className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm text-gray-700">{provider.address}</p>
                    {mapsLink && (
                      <a
                        href={mapsLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-violet-600 hover:text-violet-700 flex items-center gap-1 mt-1"
                      >
                        Open in Google Maps <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              )}
              {provider.phone && (
                <div className="flex items-center gap-3">
                  <Phone className="w-4 h-4 text-gray-400 shrink-0" />
                  <a href={`tel:${provider.phone}`} className="text-sm text-violet-600 hover:text-violet-700">
                    {provider.phone}
                  </a>
                </div>
              )}
            </div>

            {/* hours */}
            {hoursList && hoursList.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">Hours</span>
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm pl-6">
                  {hoursList.map(({ day, time }) => (
                    <div key={day} className="flex justify-between">
                      <span className="text-gray-500 w-10">{day}</span>
                      <span className="text-gray-700 text-right">{time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* score breakdown */}
            {provider.factors && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Score breakdown</p>
                <div className="space-y-1.5">
                  {[
                    { label: "Specialty", key: "specialty_match", color: "bg-violet-500" },
                    { label: "Expertise", key: "expertise_match", color: "bg-pink-500" },
                    { label: "Insurance", key: "insurance_match", color: "bg-blue-500" },
                    { label: "Location", key: "location", color: "bg-emerald-500" },
                    { label: "Availability", key: "availability", color: "bg-amber-500" },
                  ].map(({ label, key, color }) => (
                    <div key={key} className="flex items-center gap-2 text-xs">
                      <span className="w-20 text-gray-500">{label}</span>
                      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${color}`}
                          style={{ width: `${provider.factors[key] || 0}%` }}
                        />
                      </div>
                      <span className="w-8 text-right text-gray-500">{provider.factors[key] || 0}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* unverified warning */}
            {provider.unverified_factors?.length > 0 && (
              <div className="text-[11px] text-amber-600 bg-amber-50 px-3 py-2 rounded-lg">
                Unverified: {provider.unverified_factors.join(", ")}
              </div>
            )}

            {/* action buttons */}
            <div className="flex gap-2 pt-2">
              <a
                href={whatsappLink}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-[#25D366] text-white rounded-xl text-sm font-medium hover:bg-[#1da851] transition-colors"
              >
                <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
                Share on WhatsApp
              </a>
              {mapsLink && (
                <a
                  href={mapsLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-violet-600 text-white rounded-xl text-sm font-medium hover:bg-violet-700 transition-colors"
                >
                  <MapPin className="w-4 h-4" />
                  View on Map
                </a>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
