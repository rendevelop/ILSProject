from BibliographicAPI import BookEntry
from BibliographicAPI import BibliographicalAPI
from flask import Flask, render_template, request
import os

endpoint_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/conf/sets/15528919710002976/members" # Provided Endpoint URL
api_key = os.environ.get("ILS_API_KEY") # Provided API Key

# Raise error if api key not found
if api_key is None:
    raise RuntimeError("API key not provided.")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def bibliographic_results():
    """
    Returns rendered HTML template routed to the URL by Flask.

    Parameters
    ----------
        None.

    Returns
    -------
    string
        HTML Template rendered by Jinja2 with the provided context variables/placeholders.

    """
    # Create new Bibliographical API with endpoint and api key
    bib_api = BibliographicalAPI(endpoint_url, api_key)

    # Fetch the records from the provided endpoint
    bib_results = bib_api.getRecordsFromAPI(verbose=True)

    # Sort method requested in the arguments
    sort_method = request.args.get("sort_method")

    # Initialize sorted bibliographical results
    sorted_bib_results = None

    if sort_method == "descending_alphabetical":
        # Sort By Alphabetical Order Descending
        sorted_bib_results = BibliographicalAPI.sortRecordsByTitle(bib_results, descending=True)
    elif sort_method == "ascending_publish_date":
        # Sort By Publish Date Ascending
        sorted_bib_results = BibliographicalAPI.sortRecordsByPublishDate(bib_results, descending=False)
    elif sort_method == "descending_publish_date":
        # Sort By Publish Date Descending
        sorted_bib_results = BibliographicalAPI.sortRecordsByPublishDate(bib_results, descending=True)
    else:
        # Sort By Alphabetical Order Ascending by Default
        sorted_bib_results = BibliographicalAPI.sortRecordsByTitle(bib_results, descending=False)

    # Render the results to the provided template with sort method
    rendered_template = render_template("template.html", bib_results=sorted_bib_results, sort_method=sort_method)

    # Write to HTML file
    with open("results.html", "w", encoding="utf=8") as fw:
        fw.write(rendered_template)
    
    return rendered_template

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)



