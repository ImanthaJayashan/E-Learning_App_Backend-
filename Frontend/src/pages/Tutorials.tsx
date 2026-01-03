import Navbar from "../components/Navbar";
import PrimaryButton from "../components/PrimaryButton";
import { useNavigate } from "react-router-dom";

const wordFamilies = {
  "AT Family": ["CAT", "BAT", "HAT", "MAT", "RAT", "FAT"],
  "AN Family": ["CAN", "MAN", "FAN", "PAN", "VAN"],
  "AP Family": ["CAP", "MAP", "NAP", "TAP"],
  "ET Family": ["PET", "GET", "MET", "LET", "SET", "VET"],
  // ... add more using the file list
};

export default function Tutorials() {
  const nav = useNavigate();
  return (
    <div>
      <Navbar />
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-extrabold text-kidpurple">
            Tutorials — Short Vowel Families
          </h2>
          <PrimaryButton onClick={() => nav("/")}>Back Home</PrimaryButton>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {Object.entries(wordFamilies).map(([family, words]) => (
            <div key={family} className="bg-white p-4 rounded-2xl shadow-lg">
              <h3 className="font-bold text-xl">{family}</h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {words.map((w) => (
                  <div
                    key={w}
                    className="px-3 py-2 bg-kidteal/10 rounded-full font-semibold"
                  >
                    {w}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
