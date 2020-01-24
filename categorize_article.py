from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


def _categorize_article(text, confidence_thresh=0.69):
    # Instantiates a client
    client = language.LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    res = client.classify_text(document)
    print(res)
    return [tag.name for tag in res.categories if tag.confidence > confidence_thresh]

def tag_article(data, context):
    pass

text = """
The House managers are completing their opening arguments in the case against President Trump and describing his efforts to cover up his conduct. The trial will last until the Democrats wrap up their arguments or they have reached the end of their allotted 24 hours. Here’s what to expect.

Democrats have one last chance to persuade Republicans to pursue additional witnesses and documents. There are a handful of Republicans who could break with their party. Senators have already heard almost 16 hours of arguments from the managers, all Democrats who are acting as prosecutors, and fatigue is setting in.

The president has not appeared in the Capitol, but he looms large because the managers are using Mr. Trump’s own words against him. Mr. Trump spoke at an anti-abortion rally on the National Mall just after noon, and his lawyers plan to begin their defense on Saturday morning, using only a few hours of the day.

In some of his most confrontational comments yet, Representative Adam B. Schiff of California, the chairman of the House Intelligence Committee, laid out President Trump’s refusal to accept the conclusion of American intelligence agencies that Russia, not Ukraine, interfered in the 2016 presidential elections as a betrayal of the nation’s foreign policy.

“I don’t know if there’s ever been a greater success of Russian intelligence,” Mr. Schiff said. “Whatever profile Russia did of our president, boy, did they have him spot on.”

Mr. Schiff said that the president’s defense of Russia in 2018, as he stood in Helsinki next to President Vladimir V. Putin of Russia, amounted to “one hell of a Russian intelligence coup.”
"""

print(_categorize_article(text))