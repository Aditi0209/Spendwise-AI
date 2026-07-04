from services.rag import retrieve_context

def run_rag(query: str):
    context = retrieve_context(query)
    return context if context else ["General financial guidance applies."]