"""Error-handling and behaviour tests: python test_chatbot.py"""
import os
os.environ["LLM_PROVIDER"] = "offline"
import engine as E
import llm_client

bot = E.TvastrEngine()
def check(name, cond):
    print(("PASS" if cond else "FAIL"), "-", name)
    return cond

ok = True
ok &= check("empty input handled", bot.respond("   ")["source"] == "validation")
ok &= check("too-long input handled", bot.respond("a" * 2000)["source"] == "validation")
ok &= check("greeting handled", "TVASTR" in bot.respond("hello")["reply"])
ok &= check("out-of-scope handled", bot.respond("what is the capital of France")["intent"] is None)
ok &= check("gibberish handled", bot.respond("asdfghjkl")["intent"] is None)
ok &= check("lighting intent", bot.respond("How can I light an interview with one LED?")["intent"] == "lighting")
ok &= check("editing intent", bot.respond("How should I cut this scene to the beat?")["intent"] == "editing")
r = bot.respond("Give me shots for my night hip-hop music video with a car")
ok &= check("context detected", "night" in r["context"].get("setting", []) and "hip-hop" in r["context"].get("genre", []))
r2 = bot.respond("how do I light it?", ctx=r["context"])
ok &= check("context remembered across turns", "hip-hop" in r2["context"].get("genre", []))

# LLM failure -> graceful fallback (simulate API down)
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["GEMINI_API_KEY"] = "fake"
def boom(*a, **k): raise llm_client.LLMError("The AI service is having trouble right now.")
E.generate = boom
r = bot.respond("How do I fix flat footage?")
ok &= check("LLM failure falls back to built-in guidance", r["source"] == "fallback" and "Note:" in r["reply"])
print("\nALL TESTS PASSED" if ok else "\nSOME TESTS FAILED")
