import sort_documents
import tag_article
import analyze_invoice
import analyze_form

def sort_documents_entry(data, context):
    sort_documents.sort_documents(data, context)

def tag_article_entry(data, context):
    tag_article.tag_article(data, context)


def analyze_form_entry(data, context):
    analyze_form.analyze_form(data, context)
