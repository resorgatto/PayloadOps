import { Moon, Sun } from "lucide-react"
import { useTheme } from "../lib/theme"
import styles from "./ThemeToggle.module.css"

export function ThemeToggle() {
    const { theme, setTheme } = useTheme()

    const toggleTheme = () => {
        if (theme === "light") {
            setTheme("dark")
        } else {
            setTheme("light")
        }
    }

    return (
        <button
            className={styles.toggleBtn}
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title="Toggle theme"
        >
            {theme === "light" ? (
                <Sun size={18} />
            ) : (
                <Moon size={18} />
            )}
        </button>
    )
}
