from ddgs import DDGS

def web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No results found."

        formatted=[]    
        for r in results:
            formatted.append(
                f"Title: {r['title']}\n"
                f"URL: {r['href']}\n"
                f"Summary: {r['body']}\n"
            )

        return "\n---\n".join(formatted)
    
    except Exception as e:
        return f"Search error: {str(e)}"