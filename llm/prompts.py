"""Centralized prompt templates. Never build prompts inline elsewhere."""

SYSTEM_PROMPT = (
    "Tu es Trovare, un assistant qui aide deux utilisateurs à chercher un "
    "appartement à louer. Réponds en français, de façon concise et utile. "
    "La conversation est partagée entre les deux utilisateurs ; leurs messages "
    "sont préfixés par leur prénom pour que tu puisses les distinguer."
)

RESET_WARNING = (
    "\n\n⚠️ La conversation approche de sa limite d'historique et sera "
    "bientôt réinitialisée automatiquement. Utilisez `/new` si vous voulez "
    "repartir de zéro maintenant, ou continuez — la réinitialisation se fera "
    "automatiquement le moment venu."
)

RESET_NOTICE = (
    "\n\n🔄 L'historique de conversation a atteint sa limite et vient d'être "
    "réinitialisé automatiquement."
)
