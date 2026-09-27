import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0b0f19",
        surface: "#111827",
        "surface-raised": "#1e293b",
        "surface-subtle": "#0f172a",
        border: "#1e293b",
        "border-subtle": "#334155",
        primary: {
          DEFAULT: "#38bdf8",
          hover: "#0284c7",
          subtle: "rgba(56, 189, 248, 0.1)",
        },
        secondary: {
          DEFAULT: "#818cf8",
          subtle: "rgba(129, 140, 248, 0.1)",
        },
        success: {
          DEFAULT: "#10b981",
          subtle: "rgba(16, 185, 129, 0.1)",
        },
        warning: {
          DEFAULT: "#f59e0b",
          subtle: "rgba(245, 158, 11, 0.1)",
        },
        danger: {
          DEFAULT: "#ef4444",
          subtle: "rgba(239, 68, 68, 0.1)",
        },
      },
    },
  },
  plugins: [],
};
export default config;
