from leetscrape import GetQuestion

def print_question(slug: str):
    # Fetch the question data
    q = GetQuestion(titleSlug=slug).scrape()
    
    # Title and metadata
    print("== Question ==", q.title if hasattr(q, "title") else "")
    if hasattr(q, "difficulty"):
        print("Difficulty:", q.difficulty)
    if hasattr(q, "likes"):
        print("Likes:", q.likes)
    print()
    
    # Problem statement (HTML or text)
    if hasattr(q, "Body"):
        print("---- Statement ----")
        print(q.Body)
    elif hasattr(q, "content"):
        print("---- Statement ----")
        print(q.content)
    else:
        print("No statement field found.")
    print()
    
    # Code stub / starter code
    print("---- Starter Code ----")
    # many versions use `Code`, or `codeSnippets`
    if hasattr(q, "Code"):
        print(q.Code)
    elif hasattr(q, "codeSnippets"):
        # codeSnippets might be a list of dicts
        for snippet in q.codeSnippets:
            lang = snippet.get("lang")
            code = snippet.get("code")
            print(f"--- {lang} ---")
            print(code)
    else:
        print("No code stub field found.")
    print()
    
    # Sample test cases (if available)
    print("---- Sample Tests ----")
    if hasattr(q, "TestCases"):
        # sometimes stored in q.TestCases or q.sampleTests
        print(q.TestCases)
    elif hasattr(q, "testCases"):
        print(q.testCases)
    elif hasattr(q, "examples"):
        # maybe examples is a list of (input, output)
        for ex in q.examples:
            print(ex)
    else:
        print("No sample tests field found.")
    print()
    
    # Hints / explanation / other metadata
    print("---- Hints / More Info ----")
    if hasattr(q, "Hints"):
        print(q.Hints)
    if hasattr(q, "topicTags"):
        print("Topics:", q.topicTags)
    if hasattr(q, "isPaidOnly"):
        print("Paid only:", q.isPaidOnly)
    print()

if __name__ == "__main__":
    slug = "Longest-Common-Prefix"  # change this to any problem slug
    print_question(slug)
