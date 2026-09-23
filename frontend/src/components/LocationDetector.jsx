import { useState } from "react";
import { MapPin, Loader2, X } from "lucide-react";

export default function LocationDetector({ city, onCityDetected }) {
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState("");

  const detect = async () => {
    if (!navigator.geolocation) {
      setError("Geolocation not supported");
      return;
    }

    setDetecting(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json&accept-language=en`,
            { headers: { "User-Agent": "SakhiHealthNavigator/1.0" } }
          );
          const data = await res.json();
          const addr = data.address || {};
          const detected = addr.city || addr.town || addr.village || addr.county || "";
          if (detected) {
            onCityDetected(detected);
          } else {
            setError("Couldn't detect city");
          }
        } catch {
          setError("Detection failed");
        } finally {
          setDetecting(false);
        }
      },
      () => {
        setError("Location access denied");
        setDetecting(false);
      },
      { enableHighAccuracy: false, timeout: 10000 }
    );
  };

  if (city) {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-700">
        <MapPin className="w-3.5 h-3.5" />
        <span>{city}</span>
        <button
          onClick={() => onCityDetected("")}
          className="ml-1 p-0.5 hover:bg-emerald-100 rounded"
        >
          <X className="w-3 h-3" />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={detect}
        disabled={detecting}
        className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-600 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
      >
        {detecting ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
        ) : (
          <MapPin className="w-3.5 h-3.5" />
        )}
        <span>{detecting ? "Detecting..." : "My location"}</span>
      </button>
      {error && <span className="text-[10px] text-red-500">{error}</span>}
    </div>
  );
}
