import Navbar from "../components/Navbar";
import PrimaryButton from "../components/PrimaryButton";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const nav = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-kidblue via-kidteal to-peach">
      <Navbar />
      <main className="max-w-6xl mx-auto p-8">
        <section className="bg-white/80 backdrop-blur-xl rounded-big p-10 shadow-glow ring-4 ring-kidpurple/20">
          <h1 className="text-5xl font-extrabold text-kidpurple text-center">
            Pick the Letter
          </h1>
          <p className="mt-4 text-center text-lg text-gray-600">
            Short, big letters — perfect for tiny hands. Play tutorial or try
            the quiz.
          </p>

          <div className="mt-8 flex items-center justify-center gap-6">
            <PrimaryButton onClick={() => alert("Quiz page coming soon!")}>
              Start Quiz
            </PrimaryButton>
            <button
              onClick={() =>
                alert("Tutorial coming — play videos & practice writing!")
              }
              className="px-6 py-3 rounded-full bg-kidpink text-white font-bold"
            >
              Tutorial
            </button>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-4">
            <div className="bg-kidblue/20 p-6 rounded-xl text-center">
              <h3 className="font-bold text-2xl text-kidblue">For kids 4–7</h3>
              <p className="mt-2 text-sm text-gray-600">
                Big letters, simple choices, fun colors.
              </p>
            </div>
            <div className="bg-kidteal/20 p-6 rounded-xl text-center">
              <h3 className="font-bold text-2xl text-kidteal">
                10-question quiz
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                Each question has 3 choices and a big board to write the missing
                letter.
              </p>
            </div>
            <div className="bg-kidpurple/20 p-6 rounded-xl text-center">
              <h3 className="font-bold text-2xl text-kidpurple">Reports</h3>
              <p className="mt-2 text-sm text-gray-600">
                Simple progress tracking for parents & teachers.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div >
  );
}
