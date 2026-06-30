from gemini_helper import generate_summary

text = """
Java is an object-oriented programming language.
It supports encapsulation, inheritance,
polymorphism and abstraction.
"""

result = generate_summary(text)

print(result)