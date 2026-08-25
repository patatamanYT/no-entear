import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#08090b",
          900: "#0c0e12",
          850: "#111318",
          800: "#15181e",
          750: "#191c23",
          700: "#20242c",
          600: "#2a2f39",
          500: "#3a4150",
          400: "#5b6472",
          300: "#8891a0",
          200: "#b7bfcb",
          100: "#e2e6eb",
        },
        pitch: {
          grass: "#0d3d24",
          grassLight: "#124d2d",
          line: "rgba(226, 232, 240, 0.55)",
        },
        accent: {
          DEFAULT: "#38bdf8",
          soft: "#7dd3fc",
        },
        good: "#34d399",
        bad: "#f87171",
        warn: "#fbbf24",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};

export default config;
