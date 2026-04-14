/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0D0F14",
        surface: "#161B22",
        accent: "#00D4FF",
        ink: "#E6EDF3",
        muted: "#8B949E",
      },
      boxShadow: {
        glow: "0 20px 80px rgba(0, 212, 255, 0.16)",
      },
      fontFamily: {
        heading: ["Sora", "sans-serif"],
        body: ["Sora", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        floatin: "floatin 0.45s ease-out forwards",
      },
      keyframes: {
        floatin: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
