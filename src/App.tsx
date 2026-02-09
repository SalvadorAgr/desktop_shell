import { SuggestiveSearch } from "@/components/ui/suggestive-search"
import { useEffect } from "react"

export default function App() {
    useEffect(() => {
        // Auto-focus when modal opens
        const observer = new MutationObserver(() => {
            const modal = document.getElementById('search-modal');
            if (modal && modal.style.display === 'flex') {
                const input = document.querySelector('#search-react-root input');
                if (input instanceof HTMLInputElement) {
                    setTimeout(() => input.focus(), 100);
                }
            }
        });

        const modal = document.getElementById('search-modal');
        if (modal) {
            observer.observe(modal, { attributes: true, attributeFilter: ['style'] });
        }

        return () => observer.disconnect();
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            const value = (e.currentTarget as HTMLInputElement).value.trim();
            if (value) {
                // @ts-ignore - addNewTab is a global function in index.html
                window.addNewTab(`https://www.google.com/search?q=${encodeURIComponent(value)}`);
                const searchModal = document.getElementById('search-modal');
                if (searchModal) {
                    searchModal.style.display = 'none';
                }
                (e.currentTarget as HTMLInputElement).value = '';
            }
        } else if (e.key === 'Escape') {
            const searchModal = document.getElementById('search-modal');
            if (searchModal) {
                searchModal.style.display = 'none';
            }
        }
    };

    return (
        <div className="w-full">
            <SuggestiveSearch
                suggestions={[
                    "Find trending topics",
                    "Search the web...",
                    "Discover something new",
                    "What are you looking for?",
                ]}
                effect="typewriter"
                className="w-full border-white/10 hover:border-white/20 transition-colors bg-transparent"
                inputClassName="text-white/90 text-base h-12"
                typeDurationMs={800}
                pauseAfterTypeMs={2000}
                deleteDurationMs={400}
                onKeyDown={handleKeyDown}
            />
        </div>
    )
}
