import { useNavigate } from "react-router-dom";
export default function Navbar() {
  const nav = useNavigate();
  return (
    <nav className="w-full bg-transparent p-4  bg-gradient-to-r from-orange-400 via-pink-400 to-yellow-400 shadow-lg mb-6">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div
          onClick={() => nav("/")}
          className="flex items-center gap-3 cursor-pointer"
        >
          <div className="bg-white/60 p-2 rounded-full">🐱</div>
          <h1 className="text-white text-2xl font-bold">WriteSense</h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => nav("/tutorials")}
            className="text font-semibold text-shite px-4 py-2 rounded-full hover:bg-white/20 transition"
          >
            Tutorials
          </button>
          <button
            onClick={() => alert("Quiz page coming soon!")}
            className="bg-kidpink text-white px-4 py-2 rounded-full font-bold shadow"
          >
            Start Quiz
          </button>
        </div>
      </div>
    </nav>
  );
}
