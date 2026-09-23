import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import ChatApp from "./pages/ChatApp";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/chat" element={<ChatApp />} />
    </Routes>
  );
}
