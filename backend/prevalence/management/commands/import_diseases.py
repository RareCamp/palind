import json

from django.core.management.base import BaseCommand
from django.db import transaction


from prevalence.models import Disease


class Command(BaseCommand):
    help = "Import diseases from a DiseaseOntology JSON file"

    def add_arguments(self, parser):
        parser.add_argument("do_json", type=str)

    def handle(self, *args, **options):
        graph = json.load(open(options["do_json"]))["graphs"][0]

        # Extract data
        version = graph["meta"]["version"]
        nodes = graph["nodes"]
        edges = graph["edges"]

        print(f"Loading version {version}")

        # Delete all diseases that are not referenced by any dataset
        Disease.objects.filter(dataset__isnull=True).delete()

        # Get the parent of all edges
        parents = [edge["obj"] for edge in edges if edge["pred"] == "is_a"]

        # Create a disease for each node that is not a parent of any other node
        with transaction.atomic():
            for node in nodes:
                if node["id"] not in parents:
                    # Do not import deprecated
                    if node.get("meta", {}).get("deprecated", False):
                        continue

                    # All diseases are classes
                    if node.get("type", "") != "CLASS":
                        continue

                    # Extract xrefs
                    xrefs = dict([x["val"].split(":") for x in node.get("meta", {}).get("xrefs", [])])

                    # Create disease
                    Disease.objects.create(
                        do_id=node["id"],
                        name=node.get("lbl", "").capitalize(),
                        description=node.get("meta", {})
                        .get("definition", {})
                        .get("val", ""),
                        do_json=node,
                        **xrefs,
                    )