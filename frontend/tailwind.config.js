/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(56, 189, 248, 0.25), 0 10px 30px rgba(2, 132, 199, 0.15)",
      },
    },
  },
  plugins: [],
};
