import React from "react";
import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Tutorials from "./pages/Tutorials";

;

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/tutorials" element={<Tutorials />} />

    </Routes>
  );
}
