/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "ui-sans-serif", "system-ui"] },
      colors: {
        ink: "#0F172A",
        surface: "#F5F7FB",
        card: "#FFFFFF",
        primary: "#4F8EF7",
        accent: "#7C5CFF",
        muted: "#9AA4B2",
        success: "#22C55E",
        warn: "#F59E0B",
        danger: "#EF4444",
      },
      boxShadow: {
        neo: "8px 8px 24px rgba(15,23,42,.08), -6px -6px 20px rgba(255,255,255,.9)",
        soft: "0 8px 28px rgba(15,23,42,.08)",
        ring: "0 0 0 8px rgba(79,142,247,.12)",
      },
      borderRadius: { xl2: "1.25rem" },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};