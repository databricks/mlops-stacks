from cookiecutter.utils import simple_filter
import re
from urllib.parse import urlparse

AZURE_DOC_BASE = "https://learn.microsoft.com/azure/databricks"
AWS_DOC_BASE = "https://docs.databricks.com"


@simple_filter
def generate_doc_link(path, cloud):
    """Create cloud specific doc link. Usage example:

    {{ "applications/machine-learning/index.html" | generate_doc_link(cookiecutter.cloud) }}

    :param path: doc path of the documentation link in AWS. Does not begin with `/`. An Azure doc
        path (what follows `databricks/` in the URL) also works so long as it is not used to
        generate doc links for other clouds.
    :param cloud: cookiecutter cloud parameter value, i.e. `cookiecutter.cloud`

    :return: documentation links for the specified cloud
    """
    if cloud == "azure" and path == "repos/set-up-git-integration.html":
        path = "repos/repos-setup"
    baseUrl = AZURE_DOC_BASE if cloud == "azure" else AWS_DOC_BASE
    newDocsPath = path.replace(".html", "") if cloud == "azure" else path
    return f"{baseUrl}/{newDocsPath}"


@simple_filter
def regex_replace(string, regex_string, replacement):
    return re.sub(re.compile(regex_string), replacement, string)


@simple_filter
def get_host(workspace_url):
    parsed_url = urlparse(workspace_url)
    scheme = parsed_url.scheme
    hostname = parsed_url.hostname
    return f"{scheme}://{hostname}"
