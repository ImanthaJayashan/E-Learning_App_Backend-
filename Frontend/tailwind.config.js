export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      borderRadius: {
        big: "2rem",
        xl2: "1.25rem",
      },
      colors: {
        kidpurple: "#7C3AED",
        kidblue: "#60A5FA",
        kidteal: "#10B981",
        kidpink: "#FB7185",
        peach: "#FFF6EE",
      },
      boxShadow: {
        "soft-lg": "0 20px 40px rgba(0,0,0,0.12)",
        glow: "0 8px 30px rgba(124, 58, 237, 0.18)",
      },
    },
  },
  plugins: [],
};
