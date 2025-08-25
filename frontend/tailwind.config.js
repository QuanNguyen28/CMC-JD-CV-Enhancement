// tailwind.config.cjs
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b1220",
        card: "#0e1627",
        primary: "#6d8dff",
        accent: "#22d3ee",
        text: "#e5e7eb",
        muted: "#9aa4b2",
        success: "#22c55e",
        danger: "#ef4444",
        warning: "#f59e0b",
      },
      fontFamily: {
        display: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        "neo-lg":
          "16px 16px 32px rgba(0,0,0,.55), -14px -14px 30px rgba(255,255,255,.04)",
        "neo":
          "12px 12px 24px rgba(0,0,0,.5), -10px -10px 22px rgba(255,255,255,.04)",
        "neo-sm":
          "8px 8px 16px rgba(0,0,0,.45), -6px -6px 14px rgba(255,255,255,.04)",
        inset:
          "inset 6px 6px 14px rgba(0,0,0,.45), inset -6px -6px 14px rgba(255,255,255,.04)",
      },
      borderRadius: { neo: "18px" },
    },
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/typography")],
};