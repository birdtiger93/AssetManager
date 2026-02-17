/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#3b82f6",
                secondary: "#64748b",
                dark: "#1e293b",
                success: "#22c55e",
                danger: "#ef4444",
            }
        },
    },
    plugins: [],
}
